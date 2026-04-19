from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from locations.models import VisitSegment


class Command(BaseCommand):
    help = "Dedupe VisitSegments by merging overlapping segments per user/place."

    def add_arguments(self, parser):
        parser.add_argument("--user-id", type=int, required=False)
        parser.add_argument("--place-id", type=int, required=False)
        parser.add_argument("--touch-seconds", type=int, default=0)  # merge if gap <= this
        parser.add_argument("--dry-run", action="store_true", default=False)

    @transaction.atomic
    def handle(self, *args, **options):
        user_id = options.get("user_id")
        place_id = options.get("place_id")
        touch = timedelta(seconds=int(options["touch_seconds"]))
        dry_run = bool(options["dry_run"])

        qs = VisitSegment.objects.all().order_by("user_id", "place_id", "arrived_at", "id")
        if user_id:
            qs = qs.filter(user_id=user_id)
        if place_id:
            qs = qs.filter(place_id=place_id)

        total_deleted = 0
        total_merged_into = 0

        current_user_place = None
        group = []

        def flush_group(group_segments):
            nonlocal total_deleted, total_merged_into

            if not group_segments:
                return

            # Merge overlaps in this group into a list of "kept" segments
            kept = []
            for seg in group_segments:
                if not kept:
                    kept.append(seg)
                    continue

                last = kept[-1]
                last_end = last.departed_at or last.arrived_at  # treat null departed as arrived for safety
                seg_end = seg.departed_at or seg.arrived_at

                # overlap or touching?
                if seg.arrived_at <= (last_end + touch):
                    # merge into last: expand departed_at to max
                    new_end = max(last_end, seg_end)

                    if not dry_run:
                        last.departed_at = new_end
                        last.save(update_fields=["departed_at"])

                        seg.delete()
                    total_deleted += 1
                    total_merged_into += 1
                else:
                    kept.append(seg)

        # We iterate ordered and flush per (user, place)
        for seg in qs.iterator():
            key = (seg.user_id, seg.place_id)
            if current_user_place is None:
                current_user_place = key
                group = [seg]
                continue

            if key != current_user_place:
                flush_group(group)
                current_user_place = key
                group = [seg]
            else:
                group.append(seg)

        flush_group(group)

        action = "Would delete" if dry_run else "Deleted"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} {total_deleted} duplicate VisitSegments; merged_into={total_merged_into}"
            )
        )