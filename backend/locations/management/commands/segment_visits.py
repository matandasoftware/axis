from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from locations.models import LocationSample, VisitSegment, Place, VisitCandidate


def haversine_m(lat1, lon1, lat2, lon2) -> float:
    from math import radians, sin, cos, sqrt, atan2

    R = 6371000.0
    phi1 = radians(float(lat1))
    phi2 = radians(float(lat2))
    dphi = radians(float(lat2) - float(lat1))
    dlambda = radians(float(lon2) - float(lon1))

    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def find_matching_place(user, lat, lon, default_radius_m: float):
    """
    Returns (place, distance_m, effective_radius_m) or (None, None, None)
    """
    places = Place.objects.filter(
        user=user,
        latitude__isnull=False,
        longitude__isnull=False,
    )

    best = None  # (place, dist, radius)
    for p in places.iterator():
        d = haversine_m(p.latitude, p.longitude, lat, lon)
        effective_radius = float(p.radius_m) if p.radius_m is not None else float(default_radius_m)
        if d <= effective_radius:
            if best is None or d < best[1]:
                best = (p, d, effective_radius)

    if best is None:
        return None, None, None
    return best


class Command(BaseCommand):
    help = "Segment raw LocationSample data into VisitSegment rows (v1 rule-based)."

    def add_arguments(self, parser):
        parser.add_argument("--user-id", type=int, required=True)
        parser.add_argument("--from", dest="from_ts", type=str, required=False)
        parser.add_argument("--to", dest="to_ts", type=str, required=False)
        parser.add_argument("--radius-m", type=float, default=60.0)
        parser.add_argument("--min-dwell-min", type=int, default=10)
        parser.add_argument("--dry-run", action="store_true", default=False)

    def handle(self, *args, **options):
        User = get_user_model()

        user_id = options["user_id"]
        radius_m = float(options["radius_m"])
        min_dwell = timedelta(minutes=int(options["min_dwell_min"]))
        dry_run = bool(options["dry_run"])

        user = User.objects.filter(id=user_id).first()
        if not user:
            raise CommandError(f"User {user_id} not found")

        now = datetime.now(timezone.utc)
        from_ts = options.get("from_ts")
        to_ts = options.get("to_ts")

        if from_ts:
            start = datetime.fromisoformat(from_ts.replace("Z", "+00:00"))
        else:
            start = now - timedelta(hours=24)

        if to_ts:
            end = datetime.fromisoformat(to_ts.replace("Z", "+00:00"))
        else:
            end = now

        samples = (
            LocationSample.objects.filter(user=user, recorded_at__gte=start, recorded_at__lte=end)
            .order_by("recorded_at")
        )

        if not samples.exists():
            self.stdout.write(self.style.WARNING("No samples in range."))
            return

        anchor = None
        cluster_start = None
        last_in_cluster = None

        created = 0
        candidates = 0
        skipped_no_place = 0

        def close_cluster():
            nonlocal created, candidates, skipped_no_place, anchor, cluster_start, last_in_cluster

            if anchor is None or cluster_start is None or last_in_cluster is None:
                return

            dwell = last_in_cluster.recorded_at - cluster_start
            if dwell < min_dwell:
                return

            candidates += 1

            place, dist, effective_radius = find_matching_place(
                user=user,
                lat=anchor.latitude,
                lon=anchor.longitude,
                default_radius_m=radius_m,
            )

            if place is None:
                skipped_no_place += 1

                candidate_end = last_in_cluster.recorded_at
                candidate_start = cluster_start

                overlap_exists = VisitCandidate.objects.filter(
                    user=user,
                    status=VisitCandidate.STATUS_PENDING,
                    arrived_at__lte=candidate_end,
                ).filter(
                    Q(departed_at__isnull=True) | Q(departed_at__gte=candidate_start)
                ).exists()

                if overlap_exists:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Pending VisitCandidate already exists for {candidate_start} -> {candidate_end} (dwell {dwell})"
                        )
                    )
                    return

                self.stdout.write(
                    self.style.WARNING(
                        f"Unmatched visit candidate {candidate_start} -> {candidate_end} (dwell {dwell}) "
                        f"no matching Place within radius; saved as VisitCandidate for review."
                    )
                )

                if dry_run:
                    return

                VisitCandidate.objects.create(
                    user=user,
                    arrived_at=candidate_start,
                    departed_at=candidate_end,
                    latitude=anchor.latitude,
                    longitude=anchor.longitude,
                    radius_m=int(radius_m),
                    dwell_seconds=int(dwell.total_seconds()),
                    status=VisitCandidate.STATUS_PENDING,
                )
                return

            self.stdout.write(
                self.style.WARNING(
                    f"Visit candidate: place={place.id} '{place.name}' {cluster_start} -> {last_in_cluster.recorded_at} "
                    f"(dwell {dwell}, dist={dist:.1f}m <= {effective_radius:.1f}m)"
                )
            )

            overlap_exists = VisitSegment.objects.filter(
                user=user,
                place=place,
                arrived_at__lte=last_in_cluster.recorded_at,
            ).filter(
                Q(departed_at__isnull=True) | Q(departed_at__gte=cluster_start)
            ).exists()

            if overlap_exists:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping: overlapping VisitSegment exists for place={place.id} "
                        f"{cluster_start} -> {last_in_cluster.recorded_at}"
                    )
                )
                return

            self.stdout.write(
                self.style.SUCCESS(
                    f"Creating visit: place={place.id} '{place.name}' {cluster_start} -> {last_in_cluster.recorded_at}"
                )
            )

            if dry_run:
                return

            VisitSegment.objects.create(
                user=user,
                place=place,
                arrived_at=cluster_start,
                departed_at=last_in_cluster.recorded_at,
                inferred=True,
                confidence=None,
            )
            created += 1

        for s in samples.iterator():
            if anchor is None:
                anchor = s
                cluster_start = s.recorded_at
                last_in_cluster = s
                continue

            d = haversine_m(anchor.latitude, anchor.longitude, s.latitude, s.longitude)

            if d <= radius_m:
                last_in_cluster = s
                continue

            # drift: close previous cluster
            close_cluster()

            # start new cluster
            anchor = s
            cluster_start = s.recorded_at
            last_in_cluster = s

        # close last cluster
        close_cluster()

        self.stdout.write(
            self.style.SUCCESS(
                f"Segmentation run complete. candidates={candidates} created={created} skipped_no_place={skipped_no_place}"
            )
        )