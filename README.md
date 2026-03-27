# Requirement
- Python version: >= 3.12.x
- Docker 
- uv
- GNU Make(optional): dùng để viết các script build, run , ... cho gọn.
- Hệ điều hành: Windows/Linux/MacOS

# For Development & Testing

## Clone repo & setup
``` shell
git clone https://github.com/TuLe142857/DocumentHub.git
cd DocumentHub

# tạo sẵn thư mục này tránh docker tự tạo khi build(dễ dính quyền root)
mkdir -p ./backend/test_reports 

# Copy file .env từ .env.example
cp .env.example .env
```

> [!NOTE]
> Có thể giữ nguyên file `.env` giống với file `.env.example` vẫn chạy được

## Build
```shell
make build
```

Các port expose từ docker container ra máy host(Có thể chỉnh bằng `<>_PORT_EXTERNAL` trong file .env):
- NGINX: 80
- Backend: 8000
- MYSQL: 3306
- Redis: 6379
- RedisInsight(Redis Web UI): 5540
- MinIO API: 9001
- MinIO Web UI: 9001
- MailHog(SMTP server): 1025
- MailHog(Web UI): 8025

## Run test
``` shell
make test
```

## Enter docker container
```shell
# service: tên service trong docker-compose.yml/docker-compose-dev.yml
# command: lệnh chạy (mặc định là bash để mở terminal)
# Ví dụ: make enter service=backend
make enter service=<> command=<>
```

```shell
# similar to 'make enter service=backend'
make enter-backend
```

``` shell
# vào trực tiếp mysql cli bằng root account
make-enter-db
```

```shell
# Vào redis-cli(tự động đăng nhập)
make enter-redis
```

## Stop
Dừng tất cả docker container, không xóa image và volume
``` shell
make down
```

## Stop and Clean
Dừng docker container, xóa image(local image(như backend), không bao gồm các image pull từ internet(như mysql, redis, 
...)), xóa toàn bộ volume
```shell
make clean
```

# For Production

## Clone repo & setup
``` shell
git clone https://github.com/TuLe142857/DocumentHub.git
cd DocumentHub

# tạo sẵn thư mục này tránh docker tự tạo khi build(dễ dính quyền root)
mkdir -p ./backend/test_reports 

# Copy file .env từ .env.example
cp .env.example .env
```

> [!NOTE]
> Cần chỉnh sủa file .env:
> - Chỉnh giá trị `ENVIROMENT`=prod
> - Thay thế các giá trị `changethis`
> - Nhập các giá trị liên quan SMTP phù hợp

## Build
SSH to server and run:
```shell
export ENVIRONMENT=prod
export target=prod
make build
```