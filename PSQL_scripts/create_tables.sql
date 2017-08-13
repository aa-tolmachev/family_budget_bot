--текущая позиция пользователя
CREATE TABLE public.state(
   --ID INT PRIMARY KEY     NOT NULL,
   chat_id				INTEGER ,
   current_state		VARCHAR(30)
);
CREATE INDEX main ON public.state (chat_id);

--учетные данные пользователя
CREATE TABLE public.user(
   ID INT PRIMARY KEY     NOT NULL,
   chat_id				INTEGER ,
   first_name           VARCHAR(20),
   last_name            VARCHAR(20),
   personal_wallet_id			INTEGER ,
   family_id			INTEGER	,
   family_wallet_id				INTEGER ,
   created_at			DATE ,
   last_message_at		DATE
);
CREATE INDEX  ON public.user (chat_id);


--учетные данные семьи
CREATE TABLE public.family(
   ID INT PRIMARY KEY     NOT NULL,
   family_name			VARCHAR(30),
   family_owner_user_id			INTEGER
);



--данные кошелька
CREATE TABLE public.wallet(
   ID INT PRIMARY KEY     NOT NULL,
   balance				NUMERIC(10,2),
   month_transaction_fact_id	INTEGER,
   month_transaction_plan_id	INTEGER,
   created_at			DATE ,
   last_transaction_at		DATE
);



--данные фактических транзакций
CREATE TABLE public.transaction_fact(
   ID INT PRIMARY KEY     NOT NULL,
   user_id				INTEGER,
   wallet_id			INTEGER,
   transaction_type_id	INTEGER,
   summa				NUMERIC(10,2),
   date_fact			DATE

);

--данные плановых транзакций
CREATE TABLE public.transaction_plan(
   ID INT PRIMARY KEY     NOT NULL,
   user_id				INTEGER,
   wallet_id			INTEGER,
   transaction_type_id	INTEGER,
   summa				NUMERIC(10,2),
   date_plan			DATE,
   flg_done			BOOLEAN

);

--типы транзакций
CREATE TABLE public.transaction_type(
   ID INT PRIMARY KEY     NOT NULL,
   transaction_sign		VARCHAR(5),
   transaction_name		VARCHAR(50)

);

--данные по фактическим тратам за месяц
CREATE TABLE public.month_transaction_fact(
   ID INT PRIMARY KEY     NOT NULL,
   year					INTEGER,
   month				INTEGER,
   transaction_type				INTEGER,
   summa				NUMERIC(10,2)

);

--данные по плановым тратам за месяц
CREATE TABLE public.month_transaction_plan(
   ID INT PRIMARY KEY     NOT NULL,
   year					INTEGER,
   month				INTEGER,
   flg_repeat			BOOLEAN,
   day					INTEGER,
   transaction_type				INTEGER,
   summa				NUMERIC(10,2)

);



---------------------------------------

drop table public.state;


delete
from public.user;


select *
from public.state;


UPDATE public.state
SET current_state = 'ffffff'
WHERE chat_id = 3;


INSERT INTO public.state
VALUES (2, 'Bananas');