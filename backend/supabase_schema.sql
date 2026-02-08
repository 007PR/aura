-- Aura AI Supabase Schema

create table if not exists users (
  id text primary key,
  name text not null,
  sign text not null,
  dob date not null,
  birth_time time null,
  birth_place text null,
  created_at timestamptz not null default now(),
  is_premium boolean not null default false,
  messages_today integer not null default 0,
  messages_date date not null default current_date,
  receipts_today integer not null default 0,
  receipts_date date not null default current_date,
  receipts_credits integer not null default 0
);

create table if not exists orders (
  order_id text primary key,
  user_id text not null references users(id),
  item text not null,
  amount integer not null,
  currency text not null,
  razorpay_order_id text not null,
  razorpay_payment_id text null,
  status text not null default 'created',
  created_at timestamptz not null default now()
);

create index if not exists idx_orders_rzp on orders(razorpay_order_id);
