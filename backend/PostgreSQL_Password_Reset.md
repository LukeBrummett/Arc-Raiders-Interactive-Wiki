# Quick PostgreSQL Password Reset Guide

## Problem
PostgreSQL installed but we don't know the postgres user password.

## Solution: Reset Password

1. **Edit pg_hba.conf to allow trust authentication temporarily**

   File location: `C:\Program Files\PostgreSQL\15\data\pg_hba.conf`

   Change this line:
   ```
   host    all             all             127.0.0.1/32            scram-sha-256
   ```
   
   To:
   ```
   host    all             all             127.0.0.1/32            trust
   ```

2. **Restart PostgreSQL service**
   ```powershell
   Restart-Service postgresql-x64-15
   ```

3. **Connect and set password**
   ```powershell
   psql -U postgres
   ALTER USER postgres WITH PASSWORD 'postgres';
   \q
   ```

4. **Revert pg_hba.conf back to scram-sha-256**

5. **Restart service again**
   ```powershell
   Restart-Service postgresql-x64-15
   ```

6. **Test connection**
   ```powershell
   psql -U postgres -c "SELECT version();"
   # Enter password: postgres
   ```

## Alternative: Create New Superuser

Instead of resetting postgres password, create a new superuser:

```powershell
# After editing pg_hba.conf to trust (steps 1-2 above)
psql -U postgres
CREATE USER arcraiders WITH PASSWORD 'arcraiders' SUPERUSER;
CREATE DATABASE arcraiders_wiki OWNER arcraiders;
\q
```

Then update `.env`:
```
DATABASE_URL=postgresql://arcraiders:arcraiders@localhost:5432/arcraiders_wiki
```
