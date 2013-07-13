
typedef struct FanoutResponse {

    char *url;
    size_t data_size;
    char *data;

} FanoutResponse;

int Fanout_open_connection(char *server_host, int server_port, char **urls, size_t n_urls);
FanoutResponse Fanout_next_value(int fd);
void FanoutResponse_free(FanoutResponse inp);
