--------Add new col to a table
--ALTER TABLE table_name
--ADD column_name datatype;

------- Change the data type of a col
--ALTER TABLE table_name
--ALTER COLUMN column_name datatype;

------- To delete Table
--ALTER TABLE Persons
--DROP COLUMN DateOfBirth;


create table "account"
(
	acc_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
	username text unique,
	firstname text,
	lastname text,
	password text,
	mobile_num text,
	admin_prev boolean,
	address text,
	firstbill boolean
);

create table "bills"
(
  bill_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  b_userID int REFERENCES account(acc_id) ON DELETE CASCADE,
  reading int,
  date_of_bill date NOT NULL DEFAULT CURRENT_DATE,
  due_date date,
  amount decimal(8,2),
  cubic_meters int,
  status text,
  payment decimal(8,2)
);

create table "groups"
(
  g_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  g_name text,
  g_admin int REFERENCES account(acc_id) ON DELETE CASCADE
);

create table "regcode"
(
 id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
 g_id int REFERENCES groups(g_id) ON DELETE CASCADE,
 g_code text,
 unique (g_id, g_code)
);



create or replace function user_credentials(in par_id text, out text, out text, out text, out BOOLEAN) returns setof record as
$$
   select firstname,lastname,mobile_num,admin_prev from "account" where acc_id::TEXT = par_id;
$$
 language 'sql';

create or replace function register(in par_username text, in par_firstname text, in par_lastname text, in par_password text,
                                    in par_mobile text,in par_admin_prev boolean,in par_address text, in par_regkey text) returns text as
$$
  declare
    loc_res text;
    loc_grp text;

  begin
    select into loc_grp g_code from regcode where g_code = par_regkey;

    if loc_grp isnull then
      loc_res = 'Invalid Reg Code';
    else
    insert into account(username,firstname,lastname,password,mobile_num,admin_prev,address,first_time) values
      (par_username,par_firstname,par_lastname, par_password, par_mobile, par_admin_prev,par_address,TRUE );
      delete from regcode where g_code = par_regkey;
    select into loc_res acc_id from account where username = par_username;
    end if;
      return loc_res;
  end;
$$
LANGUAGE plpgsql;

create or replace function register_admin(in par_username text, in par_firstname text, in par_lastname text, in par_password text,
                                    in par_mobile text,in par_admin_prev boolean,in par_g_name text,in par_address text) returns text as
$$
  declare
    loc_res text;
    loc_user int;

  begin
    insert into account(username,firstname,lastname,password,mobile_num,admin_prev,address) values
      (par_username,par_firstname,par_lastname, par_password, par_mobile, par_admin_prev,par_address);
    select into loc_user acc_id from account where username = par_username;
    insert into groups(g_name,g_admin) values(par_g_name,loc_user);
      loc_res = 'ok';
      return loc_res;
  end;
$$
LANGUAGE plpgsql;

create or replace function login(in par_username text, in par_password text) returns text as
$$
  declare
    loc_user text;
    loc_res text;
  begin
     select into loc_user acc_id from account
       where username = par_username and password = par_password;

     if loc_user isnull then
       loc_res = 'Error';
     else
       loc_res = loc_user;
     end if;
     return loc_res;
  end;
$$
LANGUAGE plpgsql;

create or replace function username_validator(in par_username text) returns text as
$$
  declare
    loc_user text;
    loc_res text;
  begin
     select into loc_user username from account
       where username = par_username;

     if loc_user isnull then
       loc_res = 'ok';
     else
       loc_res = 'exist';
     end if;
     return loc_res;
  end;
$$
LANGUAGE plpgsql;

create or replace function get_bills(in par_id text,out int, out text, out text, out int, out numeric , out int, out text) returns setof record as
$$
   SELECT bill_id,TO_CHAR(date_of_bill, 'mm/dd/yyyy'),TO_CHAR(due_date, 'mm/dd/yyyy'),reading, amount, cubic_meters, status from bills
   where b_userID::text = par_id;
$$
 language 'sql';

create or replace function get_onebill(in par_id text, out text, out text, out int, out int, out int) returns setof record as
$$
   SELECT TO_CHAR(date_of_bill, 'Mon dd, yyyy'),TO_CHAR(due_date, 'Mon dd, yyyy'),reading, amount, cubic_meters from bills
   where bill_id::text = par_id;
$$
language 'sql';

create or replace function get_unpaid(out text, out text, out text, out decimal) returns setof record as
$$
   SELECT TO_CHAR(date_of_bill, 'Month yyyy'), lastname::text ||', '|| firstname::text AS name, amount from bills, account 
   where bills.b_userID = account.acc_id and bills.status = 'unpaid';
$$
language 'sql';

create or replace function get_allbill(in par_id text,out int, out text, out text) returns setof record as
$$
   SELECT bill_id,TO_CHAR(date_of_bill, 'mm/dd/yyyy'),TO_CHAR(due_date, 'mm/dd/yyyy') from bills
   where b_userID::text = par_id;
$$
language 'sql';

create or replace function get_names(out int, out text, out text, out text, out int) returns setof record as
$$
   select acc_id, lastname, firstname, TO_CHAR(max(date_of_bill), 'mm/dd/yyyy'), max(reading) from account, bills where admin_prev = false and acc_id = b_userid
   group by acc_id;
$$
language 'sql';

create or replace function add_bill(in par_id int, in par_date date, in par_due date, in par_reading int, in par_rate decimal) returns text as
$$
  declare
    loc_res text;
    loc_prevbill int;
  begin
     select into loc_prevbill reading from bills
       where b_userid = par_id order by date_of_bill desc limit 1;

     if loc_prevbill isnull thenhttp://127.0.0.1:5050
       insert into bills(b_userID,reading,date_of_bill,amount,cubic_meters)
       values (par_id,par_reading,par_date,0,0);
       loc_res = 'ok';
     else
       insert into bills(b_userID,reading,date_of_bill,due_date,amount,status,cubic_meters)
       values (par_id,par_reading,par_date,par_due,(par_reading-loc_prevbill)*par_rate,'Unpaid',par_reading-loc_prevbill);
       loc_res = 'ok';
     end if;
     return loc_res;
  end;
$$
LANGUAGE plpgsql;

create or replace function searchbill(in par_name text, out int, out TEXT, out text, out text) returns setof record as
  $$
    select acc_id, firstname, lastname, address from account where concat(firstname, ' ',lastname) ilike par_name and admin_prev = False
  $$
   language 'sql';

create or replace function get_selected_date(in par_id text, out int, out text, out text, out decimal, out text, out int) returns setof record as
  $$
    select reading, TO_CHAR(date_of_bill, 'MonthDD, YYYY'),TO_CHAR(due_date, 'MonthDD, YYYY'), amount, status, cubic_meters from bills where date_of_bill = (select max(date_of_bill) from bills where b_userid::text = par_id);
  $$
language 'sql';


--THIS SELECTS THE LATEST BILL INSERTED
-- select * from bills
-- where date_of_bill = (select max(date_of_bill) from bills)

-- select reading from bills
-- where b_userid = 1
-- order by date_of_bill desc
-- limit 1

