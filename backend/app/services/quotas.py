from datetime import datetime, timezone

from fastapi import HTTPException

from app.core.config import settings
from app.models.entities import PlanType


def enforce_quota(
    plan_type: PlanType,
    usage_total: int,
    monthly_usage: int,
    monthly_reset_date: datetime | None,
) -> None:
    if plan_type == PlanType.GUEST and usage_total >= settings.guest_clip_limit:
        raise HTTPException(status_code=403, detail="Guest limit reached. Create an account to continue.")

    if plan_type == PlanType.FREE and usage_total >= settings.free_clip_limit:
        raise HTTPException(status_code=403, detail="Free plan limit reached. Upgrade via Stripe.")

    if plan_type == PlanType.PAID:
        now = datetime.now(tz=timezone.utc)
        if monthly_reset_date and now >= monthly_reset_date:
            return
        if monthly_usage >= settings.paid_monthly_limit:
            raise HTTPException(status_code=403, detail="Monthly paid quota reached.")
