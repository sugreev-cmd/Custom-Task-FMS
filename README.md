# Custom Task FMS

EA & PC Task FMS ka **fully customizable + secured** version. Saara logic same hai — sirf naam, roles,
categories aur week-off ab app ke andar se badle ja sakte hain, aur data ab Supabase Auth se protected hai.

**Live:** https://sugreev-cmd.github.io/Custom-Task-FMS/

---

## Kya customize hota hai

| # | Feature | Kahan se badlein |
|---|---------|------------------|
| 1 | **App ka naam** — title, login screen, header, emails, browser tab | Settings → 🏷 Brand |
| 2 | **5 roles**, sabke naam / icon / access editable | Settings → 🔐 Roles |
| 3 | **Categories** editable — rename karne par purane tasks bhi update ho jate hain | Settings → 📂 Categories |
| 4 | **Weekly off** — koi bhi din(s) chun sakte hain, kabhi bhi badal sakte hain | Settings → 🗓 Week Off |
| 5 | **Special working days** — off rule ko kisi ek date ke liye override karein | Settings → 🗓 Week Off |
| 6 | **Database + login emails**, apna password change | Settings → 🗄 Data |

Baaki sab bilkul EA-PC FMS jaisa: Dashboard, Tasks, MIS Report, recurring task generation
(Daily / Weekly / Monthly / Quarterly / Annual), holiday import (Excel/CSV), proof links,
Resend email alerts, dark/light theme, month + date-range filters.

---

## 🔒 Security model

Purane FMS me anon key hi sab kuch kar sakti thi — aur wo key browser me chali jati hai,
matlab jiske paas key hai wo data padh/likh/delete kar sakta tha.

Is FMS me aisa nahi hai:

- Har role ka **apna Supabase Auth account** hai (email + password, password Supabase me hashed hai — is file me kahin nahi).
- Login par app Supabase se **access token** leta hai; har database request usi token se jati hai.
- RLS policy sirf `authenticated` role ko allow karti hai. `anon` se **saare rights revoke** kar diye gaye hain.
- Token 1 ghante me expire hota hai aur apne aap refresh ho jata hai. Refresh fail hone par turant logout.

Iska matlab: sirf anon key se koi bahar wala banda kuch nahi kar sakta — verify kiya gaya hai
(anon read aur write dono `401 permission denied` dete hain).

```sql
alter table public.task_fms_tasks enable row level security;
alter table public.task_fms_tasks force row level security;

create policy "authenticated read"   on public.task_fms_tasks for select to authenticated using (true);
create policy "authenticated insert" on public.task_fms_tasks for insert to authenticated with check (true);
create policy "authenticated update" on public.task_fms_tasks for update to authenticated using (true) with check (true);
create policy "authenticated delete" on public.task_fms_tasks for delete to authenticated using (true);

revoke all on public.task_fms_tasks from anon;
grant select, insert, update, delete on public.task_fms_tasks to authenticated;
```

### Login accounts

| Role | Login email |
|------|-------------|
| Role 1 | `fms-r1@astorialiving.org` |
| Role 2 | `fms-r2@astorialiving.org` |
| Role 3 | `fms-r3@astorialiving.org` |
| Role 4 | `fms-r4@astorialiving.org` |
| Role 5 | `fms-r5@astorialiving.org` |

Passwords **is repo me nahi hain** — alag se share kiye gaye hain. Har role apna password
Settings → 🗄 Data → *Change My Password* se badal sakta hai (ya Supabase Dashboard → Authentication se).

---

## Access levels

- **Full** — sab categories, Settings, proof links, koi bhi task delete.
- **Team** — sirf apni selected categories, edit kar sakta hai, sirf apne custom tasks delete.
- **View** — sab dikhega par kuch bhi edit nahi.

Kam se kam ek role **Full** hona zaruri hai (system khud check karta hai).

---

## Week off kaise kaam karta hai

- **Weekly Off** ke din + **Holidays** ki dates → working day nahi.
- Due date agar off day pe padi to **pichhle working day** pe shift ho jayegi.
- **Special Working Days** har rule ko override karti hain.
- Saare 7 din off nahi kiye ja sakte.

> Week-off badalne se **pehle se bane tasks ki due date nahi badlegi** — sirf naye/recurring tasks pe apply hoga.

---

## Data safety

- Role rename se data pe koi asar nahi — internally role keys (`r1`…`r5`) fixed hain.
- Category rename par purane tasks ka category naam Supabase me automatically update ho jata hai.
- Settings browser ke localStorage me (`taskfms_settings_v1`), tasks Supabase me (`task_fms_tasks`).

---

## Deploy

Single file — `index.html`. GitHub Pages, Netlify, ya kisi bhi static host pe chalega.

Base: [-EA-PC-Task-FMS](https://github.com/sugreev-cmd/-EA-PC-Task-FMS)
