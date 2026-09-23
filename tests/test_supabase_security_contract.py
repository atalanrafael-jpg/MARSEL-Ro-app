from pathlib import Path

def test_profiles_role_cannot_be_self_escalated():
    sql = Path("supabase/migrations/20260920120000_harden_profiles_role_self_update.sql").read_text(
        encoding="utf-8"
    )
    assert "drop policy if exists profiles_self_update" in sql.lower()
    assert "role = (select p.role from public.profiles p where p.id = (select auth.uid()))" in sql.lower()
