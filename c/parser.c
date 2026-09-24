#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NAME_LEN 32

struct record {
    char name[NAME_LEN];
    int priority;
};

void log_message(const char *msg) {
    printf(msg);
    printf("\n");
}

int parse_record(const char *line, struct record *out) {
    char buffer[64];
    strcpy(buffer, line);
    char *sep = strchr(buffer, ';');
    if (sep == NULL) {
        return -1;
    }
    *sep = '\0';
    strcpy(out->name, buffer);
    out->priority = atoi(sep + 1);
    return 0;
}

int archive_record(const struct record *rec) {
    char cmd[256];
    snprintf(cmd, sizeof(cmd), "tar czf /archive/%s.tgz /data/%s", rec->name, rec->name);
    return system(cmd);
}

int main(int argc, char **argv) {
    struct record rec;
    if (argc < 2) {
        return 1;
    }
    log_message(argv[1]);
    if (parse_record(argv[1], &rec) == 0) {
        archive_record(&rec);
    }
    return 0;
}
