#include <sqlite3.h>
#include <stdlib.h>

typedef void callback_t(int, char**, char**);

extern void js_callback(int, char**, char**);

static int db_callback(void* data, int argc, char** argv, char** azColName){
  js_callback(argc, argv, azColName);
  return 0;
}

char *zErrMsg = 0;

int init_db(sqlite3** db);
int destroy_db(sqlite3* db);
int exec_cmd(sqlite3* db, char* cmd);
char* get_last_error();

__attribute__ ((visibility ("default")))
void* alloc_mem(unsigned size)
{
  return malloc(size);
}

__attribute__ ((visibility ("default")))
void free_mem(void* p)
{
  free(p);
}

__attribute__ ((visibility ("default")))
int init_db(sqlite3** db)
{
  return sqlite3_open(":memory:", db);
}

__attribute__ ((visibility ("default")))
int destroy_db(sqlite3* db)
{
  return sqlite3_close(db);
}

__attribute__ ((visibility ("default")))
int exec_cmd(sqlite3* db, char* cmd)
{
  return sqlite3_exec(db, cmd, db_callback, NULL, &zErrMsg);
}

__attribute__ ((visibility ("default")))
char* get_last_error()
{
  return zErrMsg;
}

void _start() {}
