--текущая позиция пользователя
CREATE TABLE public.state(
   --ID INT PRIMARY KEY     NOT NULL,
   chat_id				INTEGER ,
   current_state		VARCHAR(30),
   state_info_1			VARCHAR(1000),
   state_info_2			VARCHAR(1000),
   state_info_3			VARCHAR(1000),
   state_info_4			VARCHAR(1000),
   state_info_5			VARCHAR(1000)
);
CREATE INDEX main ON public.state (chat_id);

--учетные данные пользователя
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
   transaction_type		VARCHAR(30),
   summa				NUMERIC(10,2),
   date_fact			TIMESTAMP

);
CREATE INDEX  ON public.transaction_fact (user_id);

--данные плановых транзакций
CREATE TABLE public.transaction_plan(
   ID serial primary key,
   user_id				INTEGER,
   wallet_id			INTEGER,
   transaction_type		VARCHAR(30),
   transaction_name		VARCHAR(100),
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
   transaction_type		VARCHAR(30),
   summa				NUMERIC(10,2)

);

--данные по плановым тратам за месяц
CREATE TABLE public.month_transaction_plan(
   ID serial primary key,
   user_id INTEGER,
   wallet_id INTEGER,
   day					INTEGER,
   transaction_name		VARCHAR(100),
   transaction_type		VARCHAR(30),
   summa				NUMERIC(10,2)

);


--данные по делам
CREATE TABLE public.tasks(
   ID serial primary key,
   user_id				INTEGER,
   family_id			INTEGER,
   task					VARCHAR(200),
   date_task			TIMESTAMP,
   flg_done				BOOLEAN

);
CREATE INDEX  ON public.tasks (user_id);

---------------------------------------
--рабочие скрипты


insert into public.wallet (balance,created_at,last_transaction_at)
VALUES (0,'20170808 1540','20170808 154030');


UPDATE public.user
SET personal_wallet_id = 1
WHERE chat_id = 84723474;


insert into public.tasks (user_id ,task , date_fact , 