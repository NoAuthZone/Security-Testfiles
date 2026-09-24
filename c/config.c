#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define KEY_LEN 32
#define VALUE_LEN 128

struct setting {
    char key[KEY_LEN];
    char value[VALUE_LEN];
};

void log_line(const char *msg) {
    printf("%s\n", msg);
}

static int is_valid_key(const char *key) {
    if (*key == '\0') {
        return 0;
    }
    for (; *key; key++) {
        if (!isalnum((unsigned char)*key) && *key != '_') {
            return 0;
        }
    }
    return 1;
}

int parse_setting(const char *line, struct setting *out) {
    const char *sep = strchr(line, '=');
    if (sep == NULL) {
        return -1;
    }
    size_t key_len = (size_t)(sep - line);
    if (key_len == 0 || key_len >= KEY_LEN || strlen(sep + 1) >= VALUE_LEN) {
        return -1;
    }
    memcpy(out->key, line, key_len);
    out->key[key_len] = '\0';
    snprintf(out->value, sizeof(out->value), "%s", sep + 1);
    return is_valid_key(out->key) ? 0 : -1;
}

int main(void) {
    char line[256];
    struct setting s;
    while (fgets(line, sizeof(line), stdin) != NULL) {
        line[strcspn(line, "\n")] = '\0';
        if (parse_setting(line, &s) == 0) {
            log_line(s.key);
        }
    }
    return 0;
}
