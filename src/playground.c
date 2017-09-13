#include <sqlite3.h>

typedef void callback_t(int, char**, char**);

static int db_callback(void* data, int argc, char** argv, char** azColName){
  int i;
  callback_t* callback;
  callback = (callback_t*)data;
  callback(argc, argv, azColName);
  return 0;
}

char *zErrMsg = 0;

extern int init_db(sqlite3** db);
extern int destroy_db(sqlite3* db);
extern int exec_cmd(sqlite3* db, char* cmd, callback_t* callback);
extern char* get_last_error();

int init_db(sqlite3** db)
{
  return sqlite3_open(":memory:", db);
}

int destroy_db(sqlite3* db)
{
  return sqlite3_close(db);
}

int exec_cmd(sqlite3* db, char* cmd, callback_t* callback)
{
  return sqlite3_exec(db, cmd, db_callback, callback, &zErrMsg);
}

char* get_last_error()
{
  return zErrMsg;
}
