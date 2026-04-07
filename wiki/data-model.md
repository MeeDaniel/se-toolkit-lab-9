# Data Model

## Database Schema

The application uses PostgreSQL with two main tables: `users` and `excursions`.

## Users Table

```sql
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    login         VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255)        NOT NULL,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    excursions    INTEGER DEFAULT 0
);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PK | Unique user identifier |
| `login` | VARCHAR(100) | UNIQUE, NOT NULL, INDEXED | User's login name (visible in UI) |
| `password_hash` | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Account creation time |
| `excursions` | INTEGER | DEFAULT 0 | Counter for user's excursions |

### Notes
- Passwords are hashed using **bcrypt** via `passlib` library
- The `login` column was renamed from `telegram_alias` during migration (legacy Telegram bot was removed)
- All users **must** have a password (no exceptions)

## Excursions Table

```sql
CREATE TABLE excursions (
    id                 SERIAL PRIMARY KEY,
    user_id            INTEGER    NOT NULL REFERENCES users(id),
    number_of_tourists INTEGER    NOT NULL,
    average_age        DOUBLE PRECISION NOT NULL,
    age_distribution   DOUBLE PRECISION,
    vivacity_before    DOUBLE PRECISION NOT NULL,
    vivacity_after     DOUBLE PRECISION NOT NULL,
    interest_in_it     DOUBLE PRECISION NOT NULL,
    interests_list     TEXT,
    created_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at         TIMESTAMP WITH TIME ZONE,
    raw_message        TEXT
);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PK | Unique excursion identifier |
| `user_id` | INTEGER | FK → users.id, NOT NULL, INDEXED | Owner of the excursion |
| `number_of_tourists` | INTEGER | NOT NULL | Total number of tourists |
| `average_age` | FLOAT | NOT NULL | Average age of tourists |
| `age_distribution` | FLOAT | NULLABLE | Standard deviation of ages (0-20 range). Higher = more diverse age group |
| `vivacity_before` | FLOAT | NOT NULL | Energy/excitement level **before** excursion (0.0 – 1.0) |
| `vivacity_after` | FLOAT | NOT NULL | Energy/excitement level **after** excursion (0.0 – 1.0) |
| `interest_in_it` | FLOAT | NOT NULL | Interest in IT topics during excursion (0.0 – 1.0) |
| `interests_list` | TEXT | NULLABLE | Space-separated keywords of tourist interests |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | When excursion was recorded |
| `updated_at` | TIMESTAMPTZ | NULLABLE | When excursion was last modified |
| `raw_message` | TEXT | NULLABLE | Original user message that created this excursion |

### Field Semantics

#### Vivacity (Energy Level)
| Value | Meaning |
|-------|---------|
| `0.0` | Completely uninterested, tired |
| `0.3` | Low energy, passive |
| `0.5` | Neutral, moderate interest |
| `0.7` | Engaged, active participation |
| `1.0` | Extremely enthusiastic, highly energetic |

#### Interest in IT
| Value | Meaning |
|-------|---------|
| `0.0` | No interest in IT topics |
| `0.3` | Slight curiosity |
| `0.5` | Moderate interest |
| `0.7` | Strong interest, asked questions |
| `1.0` | Extremely interested, deep engagement |

#### Interests List (Keywords)
- **Format:** Space-separated single words only
- **Rule:** Multi-word concepts MUST be converted to acronyms or combined words
- **Examples:**
  - ✅ Correct: `"robotics AI ML datascience CV"`
  - ❌ Wrong: `"robotics and AI"`, `"machine learning"`, `"data science"`
- **Conversion rules:**
  - "machine learning" → `ML`
  - "artificial intelligence" → `AI`
  - "data science" → `datascience`
  - "computer vision" → `CV`
  - "natural language processing" → `NLP`
  - "web development" → `webdev`

## Relationships

```
users (1) ────< excursions (N)
   │                  │
   │ id               │ user_id (FK)
```

- One user can have many excursions
- Each excursion belongs to exactly one user
- Excursions are deleted when their user is deleted (cascade via FK)
- Ownership is verified on all excursion operations (users can only access their own data)

## Indexes

| Table | Column | Index Type | Purpose |
|-------|--------|-----------|---------|
| users | id | PRIMARY | Fast lookups by ID |
| users | login | UNIQUE, INDEXED | Fast login authentication |
| excursions | id | PRIMARY | Fast lookups by ID |
| excursions | user_id | INDEXED | Fast filtering by user |
