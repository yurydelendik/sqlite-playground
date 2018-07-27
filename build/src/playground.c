#include <sqlite3.h>
#include <stdlib.h>

typedef void callback_t(int, char**, char**);

extern void js_callback(int, char**, char**);

static int db_callback(void* data, int argc, char** argv, char** azColName){
  js_callback(argc, argv, azColName);
  return 0;
}

char *zErrMsg = 0;

void* alloc_mem(unsigned size)
{
  return malloc(size);
}

void free_mem(void* p)
{
  free(p);
}

int init_db(sqlite3** db)
{
  return sqlite3_open(":memory:", db);
}

int destroy_db(sqlite3* db)
{
  return sqlite3_close(db);
}

int exec_cmd(sqlite3* db, char* cmd)
{
  return sqlite3_exec(db, cmd, db_callback, NULL, &zErrMsg);
}

char* get_last_error()
{
  return zErrMsg;
}
