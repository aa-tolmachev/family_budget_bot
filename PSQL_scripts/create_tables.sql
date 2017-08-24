--текущая позиция пользователя
CREATE TABLE public.state(
   --ID INT PRIMARY KEY     NOT NULL,
   chat_id				INTEGER ,
   current_state		VARCHAR(30)
);
CREATE INDEX main ON public.state (chat_id);

--учетные данные пользователя
drop table public.user
CREATE TABLE public.user(
   ID serial primary key,
   chat_id				INTEGER ,
   first_name           VARCHAR(20),
   last_name            VARCHAR(20),
   personal_wallet_id			INTEGER ,
   family_id			INTEGER	,
   family_wallet_id				INTEGER ,
   created_at			TIMESTAMP ,
   last_message_at		TIMESTAMP
);
CREATE INDEX  ON public.user (chat_id);


--учетные данные семьи
CREATE TABLE public.family(
   ID serial primary key,
   family_name			VARCHAR(30),
   family_owner_user_id			INTEGER,
   family_users			VARCHAR(50)
);



--данные кошелька
CREATE TABLE public.wallet(
   ID serial primary key,
   balance				NUMERIC(10,2),
   created_at			TIMESTAMP ,
   last_transaction_at		TIMESTAMP
);



--данные фактических транзакций
CREATE TABLE public.transaction_fact(
   ID serial primary key,
   user_id				INTEGER,
   wallet_id			INTEGER,
   transaction_type_id	INTEGER,
   summa				NUMERIC(10,2),
   date_fact			TIMESTAMP

);

--данные плановых транзакций
CREATE TABLE public.transaction_plan(
   ID serial primary key,
   user_id				INTEGER,
   wallet_id			INTEGER,
   transaction_type_id	INTEGER,
   summa				NUMERIC(10,2),
   date_plan			TIMESTAMP,
   flg_done			BOOLEAN

);

--типы транзакций
CREATE TABLE public.transaction_type(
   ID serial primary key,
   transaction_sign		VARCHAR(5),
   transaction_name		VARCHAR(50)

);

--данные по фактическим тратам за месяц
CREATE TABLE public.month_transaction_fact(
   ID serial primary key,
   wallet_id INTEGER,
   year					INTEGER,
   month				INTEGER,
   transaction_type				INTEGER,
   summa				NUMERIC(10,2)

);

--данные по плановым тратам за месяц
CREATE TABLE public.month_transaction_plan(
   ID serial primary key,
   wallet_id INTEGER,
   year					INTEGER,
   month				INTEGER,
   flg_repeat			BOOLEAN,
   day					INTEGER,
   transaction_type				INTEGER,
   summa				NUMERIC(10,2)

);

