# Custom Task FMS

EA & PC Task FMS ka **fully customizable** version. Saara logic same hai — sirf naam, roles,
categories aur week-off ab app ke andar se badle ja sakte hain. Koi code chhune ki zarurat nahi.

**Live:** https://sugreev-cmd.github.io/Custom-Task-FMS/

---

## Kya naya hai

| # | Feature | Kahan se badlein |
|---|---------|------------------|
| 1 | **App ka naam** — title, login screen, header, emails, browser tab | Settings → 🏷 Brand |
| 2 | **5 roles**, sabke naam / icon / password / access editable | Settings → 🔐 Roles |
| 3 | **Categories** editable — rename karne par purane tasks bhi update ho jate hain | Settings → 📂 Categories |
| 4 | **Weekly off** — koi bhi din(s) chun sakte hain, kabhi bhi badal sakte hain | Settings → 🗓 Week Off |
| 5 | **Special working days** — off rule ko kisi ek date ke liye override karein | Settings → 🗓 Week Off |
| 6 | **Database** — Supabase URL / key / table name editable + Test Connection | Settings → 🗄 Data |

Baaki sab bilkul EA-PC FMS jaisa hai: Dashboard, Tasks, MIS Report, recurring task generation
(Daily / Weekly / Monthly / Quarterly / Annual), holiday import (Excel/CSV), proof links,
Resend email alerts, dark/light theme, month + date-range filters.

---

## Pehli baar setup (3 steps)

### 1. Supabase me table banayein
Settings → **🗄 Data** tab kholein, wahan se SQL copy karein aur Supabase SQL Editor me run karein.
Default table name: `task_fms_tasks`

```sql
create table if not exists public.task_fms_tasks (
  id text primary key,
  section text,
  name text,
  freq text,
  due_date date,
  actual_date date,
  status text,
  assigned_to text,
  notes text,
  month_key text,
  is_custom boolean default false,
  proof_link text,
  updated_at timestamptz default now()
);

alter table public.task_fms_tasks enable row level security;
create policy "anon all" on public.task_fms_tasks for all using (true) with check (true);
```

> ⚠️ Table ka naam alag rakhein, warna EA-PC FMS ka data mix ho jayega.

### 2. Login karein
Default passwords (pehle login ke baad turant badal dein):

| Role | Password | Access |
|------|----------|--------|
| Role 1 | `admin@123` | Full — sab kuch + Settings |
| Role 2 | `role2@123` | Team — sirf apni categories |
| Role 3 | `role3@123` | Team |
| Role 4 | `role4@123` | Team |
| Role 5 | `view@123` | View only |

### 3. Apne hisab se set karein
Settings → Brand (naam) → Categories → Roles (naam + password + access) → Week Off → Team.

---

## Access levels

- **Full** — sab categories dikhengi, Settings khul sakti hai, proof links dikhte hain, koi bhi task delete kar sakta hai.
- **Team** — sirf apni selected categories ke tasks dikhenge, edit kar sakta hai, sirf apne banaye custom tasks delete kar sakta hai.
- **View** — sab dikhega par kuch bhi edit nahi hoga.

Kam se kam ek role **Full** hona zaruri hai (system khud check karta hai).

---

## Week off kaise kaam karta hai

- Jo din **Weekly Off** me select hain + jo dates **Holidays** me hain → working day nahi mane jaate.
- Kisi task ki due date agar off day pe padegi to wo **pichhle working day** pe shift ho jayegi.
- **Special Working Days** me daali gayi date har rule ko override karti hai (us din kaam hoga).
- Saare 7 din off nahi kiye ja sakte.

> Note: week-off badalne se **pehle se bane tasks ki due date nahi badlegi** — sirf naye/recurring tasks pe apply hoga.

---

## Data safety

- Role ka naam badalne se data pe koi asar nahi — internally role keys (`r1`…`r5`) fixed hain.
- Category ka naam badalne par purane tasks ka category naam bhi Supabase me automatically update ho jata hai.
- Sab settings browser ke localStorage me save hoti hain (`taskfms_settings_v1`), tasks Supabase me.

---

## Deploy

Single file — `index.html`. GitHub Pages, Netlify, ya kisi bhi static host pe chal jayega.

Base: [-EA-PC-Task-FMS](https://github.com/sugreev-cmd/-EA-PC-Task-FMS)
