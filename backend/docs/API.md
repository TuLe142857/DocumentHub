# API Documentation
> [!NOTE]  
> **Base URL:** `/api/v1`

# Table of Content
- [Các rule chung](#rule)
- [Mô tả API](#api-desc)



---

# 1. Các Rule Chung <a id="rule"></a>

## 1.1 API Request

- Tất cả request body (nếu có) sử dụng định dạng **JSON** (`Content-Type: application/json`), ngoại trừ các endpoint upload file sử dụng **multipart/form-data**.
- Các tham số phân trang (`page`, `limit`) là query parameter tùy chọn, mặc định `page=1`, `limit=10`, tối đa `limit=100`.

---

## 1.2 API Response

Tất cả response đều có cấu trúc JSON nhất quán, chia làm 3 dạng:

### 1.2.1 Response thành công — `ResponseSuccess`
> Code backend:  
> [response.py](../app/core/response.py)  
> [error_code.py](../app/core/error_code.py)  
```json
{
  "success": true,
  "data": "Any",
  "message": "String | null"
}
```

| Field     | Type                    | Mô tả                                      |
|-----------|-------------------------|--------------------------------------------|
| `success` | `boolean` (luôn `true`) | Luôn là `true` với response thành công     |
| `data`    | any                     | Dữ liệu trả về, kiểu tùy theo endpoint     |
| `message` | `string \| null`        | Thông báo tùy chọn hiển thị cho người dùng |

---

### 1.2.2 Response thành công có phân trang — `ResponsePagination`

Dùng cho các endpoint trả về danh sách, kèm metadata phân trang.

```json
{
  "success": true,
  "data": "list<Any>",
  "message": "<String | null>",
  "meta": {
    "current_page": 1,
    "per_page": 10,
    "total_items": 100,
    "total_pages": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

**Cấu trúc `meta`:**

| Field          | Type      | Mô tả                                  |
|----------------|-----------|----------------------------------------|
| `current_page` | `integer` | Trang hiện tại                         |
| `per_page`     | `integer` | Số item mỗi trang                      |
| `total_items`  | `integer` | Tổng số item                           |
| `total_pages`  | `integer` | Tổng số trang                          |
| `has_next`     | `boolean` | Có trang tiếp theo không               |
| `has_prev`     | `boolean` | Có trang trước không                   |

---

### 1.2.3 Response lỗi — `ResponseError`

```json
{
  "success": false,
  "error_code": "ERROR_CODE",
  "message": "<string | null>"
}
```

| Field        | Type                     | Mô tả                                          |
|--------------|--------------------------|------------------------------------------------|
| `success`    | `boolean` (luôn `false`) | Luôn là `false` với response lỗi               |
| `error_code` | `string`                 | Mã lỗi định danh, giúp client xử lý cụ thể     |
| `message`    | `string \| null`         | Thông báo lỗi tùy chọn hiển thị cho người dùng |

> [!NOTE]  
> Xem đầy đủ tất cả error_code(kèm với http status tương ứng): [error_code.py](../app/core/error_code.py)  
> Bảng bên dưới là một vài error code thường dùng

| Error Code                | HTTP Status | Ý nghĩa                                                                       |
|---------------------------|-------------|-------------------------------------------------------------------------------|
| `UNAUTHORIZED_ERROR`      | 401         | Chưa đăng nhập hoặc token không hợp lệ                                        |
| `LOGIN_FAILED`            | 401         | Sai thông tin đăng nhập(identity or password mismatch)                        |
| `INVALID_JWT_TOKEN`       | 401         | JWT token không hợp lệ(fake token hoặc server đã đổi thuật toán/secretkey :)) |
| `JWT_TOKEN_REVOKED`       | 401         | Token đã bị thu hồi                                                           |
| `JWT_TOKEN_EXPIRED`       | 401         | Token đã hết hạn                                                              |
| `INVALID_CREDENTIALS`     | 401         | Thông tin xác thực không hợp lệ                                               |
| `INVALID_CODE`            | 400         | OTP/code không hợp lệ hoặc đã hết hạn                                         |
| `USER_NOT_ACTIVE`         | 403         | Tài khoản bị vô hiệu hóa (banned)                                             |
| `FORBIDDEN`               | 403         | Không có quyền thực hiện thao tác này                                         |
| `RESOURCE_NOT_FOUND`      | 404         | Tài nguyên không tồn tại                                                      |
| `RESOURCE_NOT_AVAILABLE`  | 404         | Tài nguyên tồn tại nhưng không khả dụng                                       |
| `RESOURCE_ALREADY_EXISTS` | 409         | Tài nguyên đã tồn tại (trùng lặp)                                             |
| `VALIDATION_ERROR`        | 422         | Dữ liệu request không hợp lệ                                                  |

---

## 1.3 Authentication (Xác thực)

API sử dụng **JWT (JSON Web Token)** để xác thực. Sau khi đăng nhập thành công, server cấp 2 loại token:

| Token           | Mục đích                                   | Thời hạn |
|-----------------|--------------------------------------------|----------|
| `access_token`  | Dùng để xác thực mỗi request               | Ngắn hạn |
| `refresh_token` | Dùng để lấy `access_token` mới khi hết hạn | Dài hạn  |

---

### 1.3.1 Web Client

- Server tự động ghi token vào **HTTP-only Cookie** khi đăng nhập/refresh.
- Client **không cần** (và không nên) tự xử lý token — trình duyệt tự đính kèm cookie vào mỗi request.
- Cookie names: `access_token`, `refresh_token`.

---

### 1.3.2 Mobile Client

Vì mobile không dùng cookie, cần xử lý token thủ công:

**Đăng nhập:**  
Lấy `access_token` và `refresh_token` từ response body của `/api/v1/auth/login`, lưu trữ phía client.

**Gửi request cần xác thực:**  
Đính kèm `access_token` vào header:

```text
Authorization: <access_token>
```

**Refresh token:**  
Khi `access_token` hết hạn, gọi `POST /api/v1/auth/refresh` với `refresh_token` trong request body:

```json
{
  "refresh_token": "<refresh_token>"
}
```

**Đăng xuất:**  
Gọi `POST /api/v1/auth/logout` với `refresh_token` trong body để thu hồi cả 2 token:


---

# 2. Mô tả API <a id="api-desc"></a>

> [!NOTE]  
> API prefix: `/api/v1`

# Tóm tắt danh sách API

| Method & Endpoint                                                  | Description                                                  |
|:-------------------------------------------------------------------|:-------------------------------------------------------------|
| **System**                                                         | <hr>                                                         |
| `GET` `/health`                                                    | Kiểm tra trạng thái hoạt động của server                     |
| **Auth**                                                           | <hr>                                                         |
| `GET` `/api/v1/auth/whoami`                                        | Lấy thông tin cơ bản của người dùng hiện tại (yêu cầu login) |
| `POST` `/api/v1/auth/register/request`                             | Yêu cầu đăng ký (gửi email nhận OTP)                         |
| `POST` `/api/v1/auth/register/verify`                              | Xác thực OTP đăng ký                                         |
| `POST` `/api/v1/auth/register/complete`                            | Hoàn tất đăng ký và đặt thông tin tài khoản                  |
| `POST` `/api/v1/auth/login`                                        | Đăng nhập hệ thống                                           |
| `POST` `/api/v1/auth/logout`                                       | Đăng xuất và thu hồi token                                   |
| `POST` `/api/v1/auth/refresh`                                      | Làm mới Access Token                                         |
| `POST` `/api/v1/auth/forgot_password`                              | Yêu cầu khôi phục mật khẩu                                   |
| `POST` `/api/v1/auth/reset_password`                               | Đặt lại mật khẩu mới bằng OTP                                |
| **User**                                                           | <hr>                                                         |
| `GET` `/api/v1/users/me/profile`                                   | Xem thông tin cá nhân hiện tại                               |
| `PATCH` `/api/v1/users/me/profile`                                 | Cập nhật thông tin cá nhân                                   |
| `PUT` `/api/v1/users/me/avatar`                                    | Cập nhật ảnh đại diện                                        |
| `GET` `/api/v1/users/me/documents`                                 | Lấy danh sách tài liệu cá nhân đã tải lên                    |
| `GET` `/api/v1/users/me/liked_documents`                           | Lấy danh sách tài liệu đã thích                              |
| `GET` `/api/v1/users/me/collections`                               | Lấy danh sách bộ sưu tập cá nhân                             |
| `GET` `/api/v1/users/{username}/profile`                           | Xem hồ sơ công khai của người dùng khác                      |
| `GET` `/api/v1/users/{username}/documents`                         | Xem danh sách tài liệu công khai của người dùng khác         |
| **Documents**                                                      | <hr>                                                         |
| `GET` `/api/v1/documents/supported_types`                          | Lấy danh sách các định dạng file được hỗ trợ                 |
| `GET` `/api/v1/documents/max_size`                                 | Lấy dung lượng file tối đa được phép upload                  |
| `POST` `/api/v1/documents`                                         | Tải lên tài liệu mới                                         |
| `GET` `/api/v1/documents/{document_id}`                            | Xem chi tiết thông tin một tài liệu                          |
| `PATCH` `/api/v1/documents/{document_id}`                          | Cập nhật thông tin tài liệu                                  |
| `DELETE` `/api/v1/documents/{document_id}`                         | Xóa tạm thời tài liệu (vào thùng rác)                        |
| `POST` `/api/v1/documents/{document_id}/restore`                   | Khôi phục tài liệu từ thùng rác                              |
| `PUT` `/api/v1/documents/{document_id}/tags`                       | Thêm tag cho tài liệu                                        |
| `DELETE` `/api/v1/documents/{document_id}/tags`                    | Xóa tag khỏi tài liệu                                        |
| `PUT` `/api/v1/documents/{document_id}/like`                       | Thích tài liệu                                               |
| `DELETE` `/api/v1/documents/{document_id}/like`                    | Bỏ thích tài liệu                                            |
| `GET` `/api/v1/documents/{document_id}/download`                   | Lấy link tải xuống tài liệu                                  |
| `PUT` `/api/v1/documents/{document_id}/collections`                | Đồng bộ tài liệu vào các bộ sưu tập                          |
| **Categories**                                                     | <hr>                                                         |
| `GET` `/api/v1/categories`                                         | Lấy danh sách danh mục tài liệu có sẵn                       |
| **Collections**                                                    | <hr>                                                         |
| `POST` `/api/v1/collections`                                       | Tạo bộ sưu tập mới                                           |
| `GET` `/api/v1/collections/{collection_id}/items`                  | Lấy danh sách tài liệu trong một bộ sưu tập                  |
| `PATCH` `/api/v1/collections/{collection_id}`                      | Đổi tên bộ sưu tập                                           |
| `DELETE` `/api/v1/collections/{collection_id}`                     | Xóa bộ sưu tập                                               |
| `PUT` `/api/v1/collections/{collection_id}/items/{document_id}`    | Thêm tài liệu vào bộ sưu tập                                 |
| `DELETE` `/api/v1/collections/{collection_id}/items/{document_id}` | Xóa tài liệu khỏi bộ sưu tập                                 |
| **Search**                                                         | <hr>                                                         |
| `GET` `/api/v1/search`                                             | Tìm kiếm tài liệu với các bộ lọc (query, tags, category...)  |
| **Reports**                                                        | <hr>                                                         |
| `GET` `/api/v1/reports/available_reasons`                          | Lấy danh sách lý do báo cáo vi phạm                          |
| `POST` `/api/v1/reports/documents/{document_id}`                   | Báo cáo vi phạm một tài liệu                                 |
| **Admin**                                                          | <hr>                                                         |
| `GET` `/api/v1/admin/reports`                                      | (Admin) Lấy danh sách các tài liệu bị báo cáo                |
| `GET` `/api/v1/admin/reports/documents/{document_id}`              | (Admin) Xem các báo cáo chờ xử lý của một tài liệu           |
| `POST` `/api/v1/admin/reports/documents/{document_id}`             | (Admin) Xử lý báo cáo (Chấp nhận/Từ chối)                    |
| `GET` `/api/v1/admin/documents`                                    | (Admin) Quản lý danh sách toàn bộ tài liệu                   |
| `GET` `/api/v1/admin/documents/{document_id}`                      | (Admin) Xem chi tiết tài liệu hệ thống                       |
| `POST` `/api/v1/admin/documents/{document_id}/unban`               | (Admin) Gỡ chặn tài liệu                                     |
| `GET` `/api/v1/admin/users`                                        | (Admin) Quản lý danh sách người dùng                         |
| `POST` `/api/v1/admin/users/{user_id}/ban`                         | (Admin) Khóa tài khoản người dùng                            |
| `POST` `/api/v1/admin/users/{user_id}/unban`                       | (Admin) Mở khóa tài khoản người dùng                         |
| `POST` `/api/v1/admin/categories`                                  | (Admin) Tạo mới danh mục hệ thống                            |
| `PATCH` `/api/v1/admin/categories/{category_id}`                   | (Admin) Cập nhật tên danh mục                                |
| `DELETE` `/api/v1/admin/categories/{category_id}`                  | (Admin) Xóa danh mục                                         |

---

## /health

### `[GET]` `/health`

**Description**

Kiểm tra trạng thái hoạt động của server.

---

**Request**

Không có request body hay query parameter.

---

**Response**

```json
{
  "success": true,
  "data": null,
  "message": null
}
```

---

## /auth

### `[POST]` `/auth/register/request`

**Description**

Bước 1 trong luồng đăng ký. Gửi email để nhận mã OTP xác minh.

---

**Request**

```json
{
  "email": "john@example.com"
}
```

| Field   | Type     | Bắt buộc | Mô tả        |
|---------|----------|----------|--------------|
| `email` | `string` | ✅        | Email hợp lệ |

---

**Response**

`200` — Gửi OTP thành công.
```json
{
  "success": true,
  "data": null,
  "message": null
}
```

`409` — Email đã được đăng ký.
```json
{
  "success": false,
  "error_code": "RESOURCE_ALREADY_EXISTS",
  "message": "Email already exists"
}
```

`422` — Dữ liệu không hợp lệ.
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Validation error"
}
```

---

### `[POST]` `/auth/register/verify`

**Description**

Bước 2 trong luồng đăng ký. Xác minh mã OTP nhận từ email. Thành công trả về `registration_code` để dùng ở bước 3.

---

**Request**

```json
{
  "email": "john@example.com",
  "otp_code": "123456"
}
```

| Field      | Type     | Bắt buộc | Mô tả                  |
|------------|----------|----------|------------------------|
| `email`    | `string` | ✅        | Email đã dùng ở bước 1 |
| `otp_code` | `string` | ✅        | Mã OTP nhận từ email   |

---

**Response**

`200` — Xác minh thành công.
```json
{
  "success": true,
  "data": {
    "registration_code": "abc123xyz..."
  },
  "message": null
}
```

| Field               | Type     | Mô tả                               |
|---------------------|----------|-------------------------------------|
| `registration_code` | `string` | Code dùng để hoàn tất đăng ký (bước 3) |

`400` — OTP không đúng hoặc đã hết hạn.
```json
{
  "success": false,
  "error_code": "INVALID_CODE",
  "message": "OTP not match or expired"
}
```

`422` — Dữ liệu không hợp lệ.
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Validation error"
}
```

---

### `[POST]` `/auth/register/complete`

**Description**

Bước 3 trong luồng đăng ký. Hoàn tất tạo tài khoản, tự động đăng nhập và trả về token.

- **Web:** Token được ghi vào cookie tự động.
- **Mobile:** Lấy token từ `data` trong response.

---

**Request**

```json
{
  "email": "john@example.com",
  "registration_code": "abc123xyz...",
  "username": "johndoe",
  "password": "mypassword"
}
```

| Field               | Type     | Bắt buộc | Mô tả                             |
|---------------------|----------|----------|-----------------------------------|
| `email`             | `string` | ✅        | Email đã dùng ở bước 1            |
| `registration_code` | `string` | ✅        | Code nhận từ bước 2               |
| `username`          | `string` | ✅        | Tên đăng nhập mong muốn           |
| `password`          | `string` | ✅        | Mật khẩu, độ dài **8–16 ký tự**  |

---

**Response**

`200` — Đăng ký thành công.
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  },
  "message": null
}
```

`400` — `registration_code` không hợp lệ hoặc hết hạn.
```json
{
  "success": false,
  "error_code": "INVALID_CODE",
  "message": "Registration code not match or expired"
}
```

`409` — Username đã tồn tại.
```json
{
  "success": false,
  "error_code": "RESOURCE_ALREADY_EXISTS",
  "message": "Username already exist"
}
```

`422` — Dữ liệu không hợp lệ.
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Validation error"
}
```

---

### `[POST]` `/auth/login`

**Description**

Đăng nhập bằng username hoặc email.

- **Web:** Token được ghi vào cookie tự động.
- **Mobile:** Lấy token từ `data` trong response, lưu trữ phía client để dùng cho các request tiếp theo.

---

**Request**

```json
{
  "identity": "johndoe",
  "password": "mypassword"
}
```

| Field      | Type     | Bắt buộc | Mô tả                   |
|------------|----------|----------|-------------------------|
| `identity` | `string` | ✅        | Username **hoặc** email |
| `password` | `string` | ✅        | Mật khẩu               |

---

**Response**

`200` — Đăng nhập thành công.
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  },
  "message": null
}
```

`401` — Sai thông tin đăng nhập.
```json
{
  "success": false,
  "error_code": "LOGIN_FAILED",
  "message": "Identity or password not match"
}
```

`403` — Tài khoản bị banned.
```json
{
  "success": false,
  "error_code": "USER_NOT_ACTIVE",
  "message": "User is inactive(User was banned)"
}
```

`422` — Dữ liệu không hợp lệ.
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Validation error"
}
```

---

### `[POST]` `/auth/logout` 🔒

**Description**

Đăng xuất, thu hồi token (thêm vào JWT blacklist) và xóa cookie phía server.

- `access_token`: đọc tự động từ Header hoặc Cookie.
- `refresh_token`: đọc từ body (mobile) hoặc Cookie (web).

---

**Request**

```json
{
  "refresh_token": "eyJ..."
}
```

| Field           | Type             | Bắt buộc | Mô tả                                              |
|-----------------|------------------|----------|----------------------------------------------------|
| `refresh_token` | `string \| null` | ❌        | Nếu không truyền, chỉ thu hồi `access_token` |

---

**Response**

`200` — Đăng xuất thành công.
```json
{
  "success": true,
  "data": null,
  "message": null
}
```

---

### `[POST]` `/auth/refresh`

**Description**

Làm mới `access_token` khi đã hết hạn.

- **Web:** `refresh_token` được đọc tự động từ cookie, `access_token` mới cũng được ghi lại vào cookie.
- **Mobile:** Truyền `refresh_token` vào body, lấy `access_token` mới từ `data`.

---

**Request**

```json
{
  "refresh_token": "eyJ..."
}
```

| Field           | Type             | Bắt buộc | Mô tả                                    |
|-----------------|------------------|----------|------------------------------------------|
| `refresh_token` | `string \| null` | ❌        | Bắt buộc với mobile, web dùng cookie    |

---

**Response**

`200` — Làm mới thành công.
```json
{
  "success": true,
  "data": "eyJ...",
  "message": null
}
```

> `data` là `access_token` mới dạng string.

`401` — Refresh token không hợp lệ.
```json
{
  "success": false,
  "error_code": "JWT_TOKEN_REVOKED",
  "message": "JWT Token has been revoked"
}
```

`401` — Refresh token hết hạn.
```json
{
  "success": false,
  "error_code": "JWT_TOKEN_EXPIRED",
  "message": "Refresh token has been expired"
}
```

`403` — Tài khoản bị banned.
```json
{
  "success": false,
  "error_code": "USER_NOT_ACTIVE",
  "message": "User is inactive(User was banned)"
}
```

---

### `[POST]` `/auth/forgot_password`

**Description**

Gửi mã OTP về email để tiến hành đặt lại mật khẩu.

---

**Request**

```json
{
  "identity": "johndoe"
}
```

| Field      | Type     | Bắt buộc | Mô tả                   |
|------------|----------|----------|-------------------------|
| `identity` | `string` | ✅        | Username **hoặc** email |

---

**Response**

`200` — Gửi OTP thành công.
```json
{
  "success": true,
  "data": null,
  "message": null
}
```

`401` — Người dùng không tồn tại.
```json
{
  "success": false,
  "error_code": "INVALID_CREDENTIALS",
  "message": "User not found"
}
```

`422` — Dữ liệu không hợp lệ.
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Validation error"
}
```

---

### `[POST]` `/auth/reset_password`

**Description**

Đặt lại mật khẩu bằng mã OTP nhận từ email sau khi gọi `/auth/forgot_password`.

---

**Request**

```json
{
  "identity": "johndoe",
  "otp_code": "123456",
  "new_password": "newpassword"
}
```

| Field          | Type     | Bắt buộc | Mô tả                                |
|----------------|----------|----------|--------------------------------------|
| `identity`     | `string` | ✅        | Username **hoặc** email              |
| `otp_code`     | `string` | ✅        | Mã OTP nhận từ email                 |
| `new_password` | `string` | ✅        | Mật khẩu mới, độ dài **8–16 ký tự** |

---

**Response**

`200` — Đặt lại mật khẩu thành công.
```json
{
  "success": true,
  "data": null,
  "message": null
}
```

`400` — OTP không đúng hoặc đã hết hạn.
```json
{
  "success": false,
  "error_code": "INVALID_CODE",
  "message": "OTP code not matched or expired"
}
```

`401` — Người dùng không tồn tại.
```json
{
  "success": false,
  "error_code": "INVALID_CREDENTIALS",
  "message": "User not found"
}
```

`422` — Dữ liệu không hợp lệ.
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Validation error"
}
```

---

### `[GET]` `/auth/whoami` 🔒

**Description**

Lấy thông tin tài khoản đang đăng nhập. Trả về lỗi nếu chưa xác thực.

---

**Request**

Không có request body hay query parameter.

---

**Response**

`200` — Thành công.
```json
{
  "success": true,
  "data": {
    "username": "johndoe",
    "email": "john@example.com",
    "role": "USER",
    "avatar_url": "https://..."
  },
  "message": null
}
```

| Field        | Type             | Mô tả                         |
|--------------|------------------|-------------------------------|
| `username`   | `string`         | Tên đăng nhập                 |
| `email`      | `string`         | Email tài khoản               |
| `role`       | `string`         | Vai trò (`USER`, `ADMIN`, ...) |
| `avatar_url` | `string \| null` | URL ảnh đại diện              |

`401` — Chưa đăng nhập.
```json
{
  "success": false,
  "error_code": "UNAUTHORIZED_ERROR",
  "message": "User not login"
}
```

---


## /document

## /categopries

## /collections

## /reports

## /search

## /user

## /admin

