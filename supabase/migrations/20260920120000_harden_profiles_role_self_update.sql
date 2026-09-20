-- MARSEL ROAPP security hardening
-- Prevent authenticated users from changing their own application role.
drop policy if exists profiles_self_update on public.profiles;

create policy profiles_self_update on public.profiles
for update to authenticated
using ((select auth.uid()) = id)
with check (
  (select auth.uid()) = id
  and role = (select p.role from public.profiles p where p.id = (select auth.uid()))
);
