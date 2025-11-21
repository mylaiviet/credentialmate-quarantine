import csv, sys
from datetime import date
from app.core.database import SessionLocal
from app.models.user import User
from app.models.license import License
from app.models.cme_activity import CMEActivity
from app.models.cme_requirements import StateCMEBaseRequirement, ContentSpecificCME
import logging
logging.basicConfig(level=logging.CRITICAL)

db = SessionLocal()
writer = csv.writer(sys.stdout)
writer.writerow(["Provider_Email", "State", "License_Type", "Expiration", "Days_Until_Exp", "CME_Required", "CME_Earned", "Gap", "Pct", "Status", "Topics", "Activities"])

for p in db.query(User).filter(User.role == "provider").all():
    for lic in db.query(License).filter(License.user_id == p.id).all():
        sr = db.query(StateCMEBaseRequirement).filter(StateCMEBaseRequirement.state_code.like(f"{lic.state}%")).first()
        trs = db.query(ContentSpecificCME).filter(ContentSpecificCME.state_code.like(f"{lic.state}%")).count()
        acts = db.query(CMEActivity).filter(CMEActivity.user_id == p.id, CMEActivity.state == lic.state).all()
        earned = sum(a.credits for a in acts)
        req = sr.total_hours_required if sr else 50
        gap = max(0, req - earned)
        pct = round((earned / req * 100) if req > 0 else 0, 1)
        days = (lic.expiration_date - date.today()).days if lic.expiration_date else 999
        stat = "EXPIRED" if days < 0 else "NON_COMPLIANT" if days < 90 and pct < 100 else "AT_RISK" if days < 90 or pct < 100 else "COMPLIANT"
        writer.writerow([p.email, lic.state, lic.license_type, lic.expiration_date.isoformat() if lic.expiration_date else "", days, req, earned, gap, pct, stat, trs, len(acts)])
db.close()
