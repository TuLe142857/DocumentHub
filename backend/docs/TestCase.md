# Danh sách các test case cho Backend

- [Test API `/auth`](#test-api-auth)
- [Test API `/documents`](#test-api-documents)
- [Test API `/collections`](#test-api-collections)
- [Test API `/categories`](#test-api-categories)
- [Test API `/search`](#test-api-search)
- [Test API `/reports`](#test-api-reports)
- [Test API `/users`](#test-api-users)
- [Test API `/admin`](#test-api-admin)

---

# Test API `/auth`

> Code: [test_auth_api.py](../tests/api/test_auth_api.py)

| Endpoint                                | Tên Test Case                    | Kịch bản kiểm thử                                                                                                    |
|-----------------------------------------|----------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `POST` `/api/v1/auth/register/request`  | `test_success`                   | Gửi yêu cầu đăng ký thành công với email hợp lệ.                                                                     |
| `POST` `/api/v1/auth/register/request`  | `test_email_already_exists`      | Trả về lỗi `RESOURCE_ALREADY_EXISTS` khi email đã tồn tại trong hệ thống.                                            |
| `POST` `/api/v1/auth/register/request`  | `test_invalid_email_format`      | Trả về lỗi `VALIDATION_ERROR` khi định dạng email sai.                                                               |
| `POST` `/api/v1/auth/register/request`  | `test_missing_email_field`       | Trả về lỗi khi bỏ trống (thiếu) trường email.                                                                        |
| <hr>                                    | <hr>                             | <hr>                                                                                                                 |
| `POST` `/api/v1/auth/register/verify`   | `test_success`                   | Xác thực OTP thành công, trả về mã `registration_code`.                                                              |
| `POST` `/api/v1/auth/register/verify`   | `test_wrong_otp`                 | Trả về lỗi `INVALID_CODE` khi mã OTP cung cấp không chính xác.                                                       |
| `POST` `/api/v1/auth/register/verify`   | `test_missing_field`             | Trả về lỗi `VALIDATION_ERROR` khi bỏ trống trường email hoặc otp_code.                                               |
| <hr>                                    | <hr>                             | <hr>                                                                                                                 |
| `POST` `/api/v1/auth/register/complete` | `test_success`                   | Hoàn tất đăng ký thành công, trả về token, và tự động set cookie (đăng nhập).                                        |
| `POST` `/api/v1/auth/register/complete` | `test_invalid_registration_code` | Trả về lỗi `INVALID_CODE` khi mã `registration_code` không hợp lệ.                                                   |
| `POST` `/api/v1/auth/register/complete` | `test_username_already_exists`   | Trả về lỗi `RESOURCE_ALREADY_EXISTS` khi username yêu cầu đăng ký đã tồn tại.                                        |
| `POST` `/api/v1/auth/register/complete` | `test_invalid_password`          | Trả về lỗi `VALIDATION_ERROR` khi mật khẩu không đạt yêu cầu độ dài.                                                 |
| <hr>                                    | <hr>                             | <hr>                                                                                                                 |
| `POST` `/api/v1/auth/login`             | `test_login_by_email_success`    | Đăng nhập thành công bằng email và mật khẩu đúng.                                                                    |
| `POST` `/api/v1/auth/login`             | `test_login_by_username_success` | Đăng nhập thành công bằng username và mật khẩu đúng.                                                                 |
| `POST` `/api/v1/auth/login`             | `test_wrong_password`            | Trả về lỗi `LOGIN_FAILED` khi mật khẩu cung cấp không đúng.                                                          |
| `POST` `/api/v1/auth/login`             | `test_nonexistent_identity`      | Trả về lỗi `LOGIN_FAILED` khi tài khoản (email/username) không tồn tại.                                              |
| `POST` `/api/v1/auth/login`             | `test_banned_user`               | Trả về lỗi `USER_INACTIVE` khi người dùng đã bị khóa (banned).                                                       |
| `POST` `/api/v1/auth/login`             | `test_missing_field`             | Trả về lỗi `VALIDATION_ERROR` khi thiếu trường identity hoặc password.                                               |
| <hr>                                    | <hr>                             | <hr>                                                                                                                 |
| `GET` `/api/v1/auth/whoami`             | `test_authenticated_cookie`      | Lấy thông tin user thành công khi request đã được xác thực (có kèm cookie).                                          |
| `GET` `/api/v1/auth/whoami`             | `test_unauthenticated`           | Trả về lỗi `UNAUTHORIZED` khi chưa đăng nhập (không có token).                                                       |
| `GET` `/api/v1/auth/whoami`             | `test_banned_user`               | Trả về lỗi `USER_INACTIVE` khi user hiện tại đã bị khóa (banned).                                                    |
| <hr>                                    | <hr>                             | <hr>                                                                                                                 |
| `POST` `/api/v1/auth/logout`            | `test_success`                   | Đăng xuất thành công, kiểm tra trả về lỗi `JWT_TOKEN_REVOKED` nếu cố dùng token cũ để gọi `/whoami` hoặc `/refresh`. |
| <hr>                                    | <hr>                             | <hr>                                                                                                                 |
| `POST` `/api/v1/auth/refresh`           | `test_success`                   | Lấy access token mới thành công từ refresh token hợp lệ và truy cập lại API yêu cầu xác thực.                        |
| `POST` `/api/v1/auth/refresh`           | `test_refresh_with_fake_token`   | Trả về lỗi `INVALID_JWT_TOKEN` khi refresh token cung cấp không hợp lệ.                                              |
| <hr>                                    | <hr>                             | <hr>                                                                                                                 |
| `POST` `/api/v1/auth/forgot_password`   | `test_success`                   | Gửi yêu cầu quên mật khẩu thành công.                                                                                |
| `POST` `/api/v1/auth/forgot_password`   | `test_nonexistent_identity`      | Trả về lỗi `INVALID_CREDENTIALS` khi tài khoản yêu cầu cấp lại mật khẩu không tồn tại.                               |
| `POST` `/api/v1/auth/forgot_password`   | `test_missing_field`             | Trả về lỗi `VALIDATION_ERROR` khi thiếu trường `identity`.                                                           |
| <hr>                                    | <hr>                             | <hr>                                                                                                                 |
| `POST` `/api/v1/auth/reset_password`    | `test_success`                   | Đặt lại mật khẩu mới thành công với mã OTP hợp lệ.                                                                   |
| `POST` `/api/v1/auth/reset_password`    | `test_wrong_otp`                 | Trả về lỗi `INVALID_CODE` khi mã OTP cung cấp không chính xác.                                                       |
| `POST` `/api/v1/auth/reset_password`    | `test_invalid_password`          | Trả về lỗi `VALIDATION_ERROR` khi mật khẩu mới không đạt yêu cầu định dạng hoặc quá ngắn.                            |

---

# Test API `/documents`

> Code: [test_document_api.py](../tests/api/test_document_api.py)

| Endpoint                                            | Tên Test Case                                        | Kịch bản kiểm thử                                                                                              |
|-----------------------------------------------------|------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| `GET` `/api/v1/documents/supported_types`           | `test_get_supported_types`                           | Lấy danh sách các định dạng file tài liệu được hỗ trợ thành công.                                              |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `GET` `/api/v1/documents/max_size`                  | `test_get_max_upload_size`                           | Lấy cấu hình dung lượng upload tối đa thành công.                                                              |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `POST` `/api/v1/documents`                          | `test_success`                                       | Tải lên tài liệu mới thành công với các tuỳ chọn (có tag/không tag, có mô tả/không mô tả).                     |
| `POST` `/api/v1/documents`                          | `test_unauthenticated`                               | Trả về lỗi `UNAUTHORIZED` khi người dùng chưa đăng nhập.                                                       |
| `POST` `/api/v1/documents`                          | `test_duplicate_title`                               | Trả về lỗi `RESOURCE_ALREADY_EXISTS` khi tên tài liệu đã tồn tại trong hệ thống.                               |
| `POST` `/api/v1/documents`                          | `test_unsupported_file_type`                         | Trả về lỗi `VALIDATION_ERROR` khi tải lên định dạng file không được hỗ trợ.                                    |
| `POST` `/api/v1/documents`                          | `test_file_to_large`                                 | Trả về lỗi `FILE_TOO_LARGE` khi dung lượng file vượt mức cho phép.                                             |
| `POST` `/api/v1/documents`                          | `test_category_not_found`                            | Trả về lỗi `RESOURCE_NOT_FOUND` khi ID của category không tồn tại.                                             |
| `POST` `/api/v1/documents`                          | `test_invalid_tags`                                  | Trả về lỗi `VALIDATION_ERROR` khi tags cung cấp không hợp lệ (chứa khoảng trắng, ký tự đặc biệt, viết hoa...). |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `GET` `/api/v1/documents/{document_id}`             | `test_guest_can_get_public_document`                 | Khách (chưa đăng nhập) lấy thông tin chi tiết tài liệu PUBLIC thành công.                                      |
| `GET` `/api/v1/documents/{document_id}`             | `test_guest_cannot_get_private_document`             | Trả về lỗi `FORBIDDEN` khi khách (chưa đăng nhập) truy cập tài liệu PRIVATE.                                   |
| `GET` `/api/v1/documents/{document_id}`             | `test_owner_can_get_own_public_document`             | Chủ sở hữu lấy thông tin chi tiết tài liệu PUBLIC của chính mình thành công.                                   |
| `GET` `/api/v1/documents/{document_id}`             | `test_owner_can_get_own_private_document`            | Chủ sở hữu lấy thông tin chi tiết tài liệu PRIVATE của chính mình thành công.                                  |
| `GET` `/api/v1/documents/{document_id}`             | `test_user_can_get_others_public_document`           | Người dùng đã đăng nhập lấy thông tin tài liệu PUBLIC của người khác thành công.                               |
| `GET` `/api/v1/documents/{document_id}`             | `test_user_cannot_get_others_private_document`       | Trả về lỗi `FORBIDDEN` khi người dùng cố truy cập tài liệu PRIVATE của người khác.                             |
| `GET` `/api/v1/documents/{document_id}`             | `test_document_not_found`                            | Trả về lỗi `RESOURCE_NOT_FOUND` khi document_id không tồn tại.                                                 |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `PATCH` `/api/v1/documents/{document_id}`           | `test_owner_can_update`                              | Chủ sở hữu cập nhật thông tin tài liệu (title, desc, visibility) thành công.                                   |
| `PATCH` `/api/v1/documents/{document_id}`           | `test_unauthenticated`                               | Trả về lỗi `UNAUTHORIZED` khi yêu cầu cập nhật tài liệu nhưng chưa đăng nhập.                                  |
| `PATCH` `/api/v1/documents/{document_id}`           | `test_stranger_cannot_update`                        | Trả về lỗi `FORBIDDEN` khi người dùng cố gắng cập nhật tài liệu của người khác.                                |
| `PATCH` `/api/v1/documents/{document_id}`           | `test_document_not_found`                            | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu cần cập nhật không tồn tại.                                       |
| `PATCH` `/api/v1/documents/{document_id}`           | `test_duplicate_title`                               | Trả về lỗi `RESOURCE_ALREADY_EXISTS` khi đổi tên trùng với một tài liệu khác của chính user.                   |
| `PATCH` `/api/v1/documents/{document_id}`           | `test_category_not_found`                            | Trả về lỗi `RESOURCE_NOT_FOUND` khi category_id mới muốn đổi sang không tồn tại.                               |
| `PATCH` `/api/v1/documents/{document_id}`           | `test_invalid_tags`                                  | Trả về lỗi `VALIDATION_ERROR` khi danh sách tags dùng để cập nhật không hợp lệ.                                |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `DELETE` `/api/v1/documents/{document_id}`          | `test_success`                                       | Đưa tài liệu vào thùng rác (xóa mềm) thành công.                                                               |
| `DELETE` `/api/v1/documents/{document_id}`          | `test_unauthenticated`                               | Trả về lỗi `UNAUTHORIZED` khi cố gắng xóa tài liệu nhưng chưa đăng nhập.                                       |
| `DELETE` `/api/v1/documents/{document_id}`          | `test_stranger_cannot_delete`                        | Trả về lỗi `FORBIDDEN` khi cố gắng xóa tài liệu thuộc về người khác.                                           |
| `DELETE` `/api/v1/documents/{document_id}`          | `test_document_not_found`                            | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu cần xóa không tồn tại.                                            |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `POST` `/api/v1/documents/{document_id}/restore`    | `test_success`                                       | Khôi phục tài liệu đã xóa (trong thùng rác) thành công.                                                        |
| `POST` `/api/v1/documents/{document_id}/restore`    | `test_unauthenticated`                               | Trả về lỗi `UNAUTHORIZED` khi cố gắng khôi phục tài liệu nhưng chưa đăng nhập.                                 |
| `POST` `/api/v1/documents/{document_id}/restore`    | `test_stranger_cannot_restore`                       | Trả về lỗi `FORBIDDEN` khi cố gắng khôi phục tài liệu của người khác.                                          |
| `POST` `/api/v1/documents/{document_id}/restore`    | `test_document_not_found`                            | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu cần khôi phục không tồn tại.                                      |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `PUT` `/api/v1/documents/{document_id}/tags`        | `test_add_tag_success`                               | Thêm một tag mới cho tài liệu thành công.                                                                      |
| `PUT` `/api/v1/documents/{document_id}/tags`        | `test_add_tag_unauthenticated`                       | Trả về lỗi `UNAUTHORIZED` khi thêm tag nhưng chưa đăng nhập.                                                   |
| `PUT` `/api/v1/documents/{document_id}/tags`        | `test_stranger_cannot_add_tag`                       | Trả về lỗi `FORBIDDEN` khi thêm tag cho tài liệu của người khác.                                               |
| `PUT` `/api/v1/documents/{document_id}/tags`        | `test_add_tag_document_not_found`                    | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu muốn thêm tag không tồn tại.                                      |
| `PUT` `/api/v1/documents/{document_id}/tags`        | `test_add_invalid_tag_name`                          | Trả về lỗi `VALIDATION_ERROR` khi tag name thêm vào không hợp lệ.                                              |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `DELETE` `/api/v1/documents/{document_id}/tags`     | `test_remove_tag_success`                            | Gỡ bỏ một tag khỏi tài liệu thành công.                                                                        |
| `DELETE` `/api/v1/documents/{document_id}/tags`     | `test_remove_tag_unauthenticated`                    | Trả về lỗi `UNAUTHORIZED` khi xóa tag nhưng chưa đăng nhập.                                                    |
| `DELETE` `/api/v1/documents/{document_id}/tags`     | `test_stranger_cannot_remove_tag`                    | Trả về lỗi `FORBIDDEN` khi gỡ tag từ tài liệu của người khác.                                                  |
| `DELETE` `/api/v1/documents/{document_id}/tags`     | `test_remove_tag_document_not_found`                 | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu cần gỡ tag không tồn tại.                                         |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `PUT` `/api/v1/documents/{document_id}/like`        | `test_like_document`                                 | Like tài liệu thành công, kiểm tra bộ đếm số like tăng thêm 1.                                                 |
| `PUT` `/api/v1/documents/{document_id}/like`        | `test_like_document_unauthenticated`                 | Trả về lỗi `UNAUTHORIZED` khi thực hiện thao tác like nhưng chưa đăng nhập.                                    |
| `PUT` `/api/v1/documents/{document_id}/like`        | `test_like_private_document_as_stranger`             | Trả về lỗi `FORBIDDEN` khi cố like một tài liệu PRIVATE của người dùng khác.                                   |
| `PUT` `/api/v1/documents/{document_id}/like`        | `test_like_document_not_found`                       | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu muốn like không tồn tại.                                          |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `DELETE` `/api/v1/documents/{document_id}/like`     | `test_unlike_document`                               | Bỏ like (Unlike) tài liệu thành công, kiểm tra bộ đếm số like giảm đi 1.                                       |
| `DELETE` `/api/v1/documents/{document_id}/like`     | `test_unlike_document_unauthenticated`               | Trả về lỗi `UNAUTHORIZED` khi unlike nhưng chưa đăng nhập.                                                     |
| `DELETE` `/api/v1/documents/{document_id}/like`     | `test_unlike_document_not_found`                     | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu muốn unlike không tồn tại.                                        |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `GET` `/api/v1/documents/{document_id}/download`    | `test_owner_can_download_own_public_document`        | Chủ sở hữu tải xuống tài liệu PUBLIC của chính mình thành công (số đếm download tăng 1).                       |
| `GET` `/api/v1/documents/{document_id}/download`    | `test_owner_can_download_own_private_document`       | Chủ sở hữu tải xuống tài liệu PRIVATE của chính mình thành công (số đếm download tăng 1).                      |
| `GET` `/api/v1/documents/{document_id}/download`    | `test_user_can_download_others_public_document`      | Người dùng đăng nhập tải xuống tài liệu PUBLIC của người khác thành công (số đếm download tăng 1).             |
| `GET` `/api/v1/documents/{document_id}/download`    | `test_user_can_not_download_others_private_document` | Trả về lỗi `FORBIDDEN` khi cố tải tài liệu PRIVATE của người khác.                                             |
| `GET` `/api/v1/documents/{document_id}/download`    | `test_guest_can_download_public_document`            | Khách tải tài liệu PUBLIC thành công (nhưng không tính số lần tải).                                            |
| `GET` `/api/v1/documents/{document_id}/download`    | `test_guest_can_not_download_private_document`       | Trả về lỗi `FORBIDDEN` khi khách cố tải tài liệu PRIVATE.                                                      |
| `GET` `/api/v1/documents/{document_id}/download`    | `test_document_not_found`                            | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu muốn tải không tồn tại.                                           |
| `GET` `/api/v1/documents/{document_id}/download`    | `test_unsupported_format`                            | Trả về lỗi `UNSUPPORTED_FILE_TYPE` khi người dùng yêu cầu tải ở định dạng mà tài liệu không hỗ trợ.            |
| <hr>                                                | <hr>                                                 | <hr>                                                                                                           |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_sync_add_document_to_collections`              | Đồng bộ (lưu) tài liệu vào nhiều collection mới thành công.                                                    |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_sync_remove_document_from_collections`         | Đồng bộ gỡ bỏ tài liệu khỏi một số collections thành công.                                                     |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_sync_replaces_existing_collections`            | Đồng bộ thành công thay thế danh sách collection cũ của tài liệu sang danh sách collection mới.                |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_sync_with_duplicate_collection_ids`            | Xử lý thành công việc đồng bộ ngay cả khi đầu vào truyền các ID collection bị trùng lặp.                       |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_unauthenticated`                               | Trả về lỗi `UNAUTHORIZED` khi yêu cầu đồng bộ collections nhưng chưa đăng nhập.                                |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_cannot_sync_into_others_collection`            | Trả về lỗi `FORBIDDEN` khi cố thêm tài liệu vào collection của người dùng khác.                                |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_cannot_syn_others_private_document`            | Trả về lỗi `FORBIDDEN` khi lấy tài liệu PRIVATE của người khác thêm vào collection của mình.                   |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_document_not_found`                            | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu muốn đồng bộ không tồn tại.                                       |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_collection_not_found`                          | Trả về lỗi `RESOURCE_NOT_FOUND` khi truyền vào một collection_id không tồn tại.                                |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_partial_collection_not_found`                  | Trả về lỗi `RESOURCE_NOT_FOUND` khi gửi danh sách collections nhưng có một phần id không tồn tại.              |
| `PUT` `/api/v1/documents/{document_id}/collections` | `test_missing_collection_ids_field`                  | Trả về lỗi `VALIDATION_ERROR` khi body request bỏ trống hoặc thiếu field `collection_ids`.                     |

---

# Test API `/collections`

> Code: [test_collection_api.py](../tests/api/test_collection_api.py)

| Endpoint                                                           | Tên Test Case                          | Kịch bản kiểm thử                                                                                                             |
|--------------------------------------------------------------------|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `POST` `/api/v1/collections`                                       | `test_success`                         | Tạo collection mới thành công.                                                                                                |
| `POST` `/api/v1/collections`                                       | `test_unauthenticated`                 | Trả về lỗi `UNAUTHORIZED` khi tạo collection nhưng chưa đăng nhập.                                                            |
| `POST` `/api/v1/collections`                                       | `test_duplicate_name`                  | Trả về lỗi `RESOURCE_ALREADY_EXISTS` khi tạo collection có tên bị trùng với collection đã có của user.                        |
| `POST` `/api/v1/collections`                                       | `test_missing_name`                    | Trả về lỗi `VALIDATION_ERROR` khi body request bỏ trống (thiếu) trường `name`.                                                |
| <hr>                                                               | <hr>                                   | <hr>                                                                                                                          |
| `PATCH` `/api/v1/collections/{collection_id}`                      | `test_success`                         | Đổi tên collection thành công.                                                                                                |
| `PATCH` `/api/v1/collections/{collection_id}`                      | `test_collection_not_found`            | Trả về lỗi `RESOURCE_NOT_FOUND` khi collection cần đổi tên không tồn tại.                                                     |
| `PATCH` `/api/v1/collections/{collection_id}`                      | `test_rename_to_existing_name`         | Trả về lỗi `RESOURCE_ALREADY_EXISTS` khi đổi tên mới trùng với một collection khác của cùng user.                             |
| `PATCH` `/api/v1/collections/{collection_id}`                      | `test_stranger_cannot_rename`          | Trả về lỗi `FORBIDDEN` khi người dùng cố gắng đổi tên collection của người khác.                                              |
| `PATCH` `/api/v1/collections/{collection_id}`                      | `test_unauthenticated`                 | Trả về lỗi `UNAUTHORIZED` khi đổi tên collection nhưng chưa đăng nhập.                                                        |
| `PATCH` `/api/v1/collections/{collection_id}`                      | `test_missing_field`                   | Trả về lỗi `VALIDATION_ERROR` khi bỏ trống trường `new_name`.                                                                 |
| <hr>                                                               | <hr>                                   | <hr>                                                                                                                          |
| `DELETE` `/api/v1/collections/{collection_id}`                     | `test_success`                         | Xoá collection thành công.                                                                                                    |
| `DELETE` `/api/v1/collections/{collection_id}`                     | `test_collection_not_found`            | Trả về lỗi `RESOURCE_NOT_FOUND` khi collection cần xoá không tồn tại.                                                         |
| `DELETE` `/api/v1/collections/{collection_id}`                     | `test_unauthenticated`                 | Trả về lỗi `UNAUTHORIZED` khi yêu cầu xoá collection nhưng chưa đăng nhập.                                                    |
| `DELETE` `/api/v1/collections/{collection_id}`                     | `test_stranger_cannot_delete`          | Trả về lỗi `FORBIDDEN` khi cố gắng xoá collection của người khác.                                                             |
| <hr>                                                               | <hr>                                   | <hr>                                                                                                                          |
| `PUT` `/api/v1/collections/{collection_id}/items/{document_id}`    | `test_add_self_public_document`        | Thêm tài liệu PUBLIC của chính user vào collection thành công.                                                                |
| `PUT` `/api/v1/collections/{collection_id}/items/{document_id}`    | `test_add_self_private_document`       | Thêm tài liệu PRIVATE của chính user vào collection thành công.                                                               |
| `PUT` `/api/v1/collections/{collection_id}/items/{document_id}`    | `test_add_other_user_public_document`  | Thêm tài liệu PUBLIC của người dùng khác vào collection của mình thành công.                                                  |
| `PUT` `/api/v1/collections/{collection_id}/items/{document_id}`    | `test_add_other_user_private_document` | Trả về lỗi `FORBIDDEN` khi cố thêm tài liệu PRIVATE của người khác vào collection.                                            |
| `PUT` `/api/v1/collections/{collection_id}/items/{document_id}`    | `test_collection_not_found`            | Trả về lỗi `RESOURCE_NOT_FOUND` khi collection_id không tồn tại.                                                              |
| `PUT` `/api/v1/collections/{collection_id}/items/{document_id}`    | `test_document_not_found`              | Trả về lỗi `RESOURCE_NOT_FOUND` khi document_id muốn thêm không tồn tại.                                                      |
| `PUT` `/api/v1/collections/{collection_id}/items/{document_id}`    | `test_stranger_cannot_add`             | Trả về lỗi `FORBIDDEN` khi cố thêm tài liệu vào collection thuộc sở hữu của người khác.                                       |
| <hr>                                                               | <hr>                                   | <hr>                                                                                                                          |
| `DELETE` `/api/v1/collections/{collection_id}/items/{document_id}` | `test_success`                         | Gỡ (xoá) tài liệu khỏi collection thành công.                                                                                 |
| `DELETE` `/api/v1/collections/{collection_id}/items/{document_id}` | `test_collection_not_found`            | Trả về lỗi `RESOURCE_NOT_FOUND` khi collection muốn gỡ tài liệu không tồn tại.                                                |
| `DELETE` `/api/v1/collections/{collection_id}/items/{document_id}` | `test_document_not_found`              | Trả về lỗi `RESOURCE_NOT_FOUND` khi document_id muốn gỡ không tồn tại.                                                        |
| `DELETE` `/api/v1/collections/{collection_id}/items/{document_id}` | `test_stranger_cannot_remove`          | Trả về lỗi `FORBIDDEN` khi cố gỡ tài liệu khỏi collection thuộc sở hữu của người khác.                                        |
| `DELETE` `/api/v1/collections/{collection_id}/items/{document_id}` | `test_unauthenticated`                 | Trả về lỗi `UNAUTHORIZED` khi gỡ tài liệu khỏi collection nhưng chưa đăng nhập.                                               |
| <hr>                                                               | <hr>                                   | <hr>                                                                                                                          |
| `GET` `/api/v1/collections/{collection_id}/items`                  | `test_success`                         | Lấy danh sách tài liệu trong collection thành công (hỗ trợ phân trang).                                                       |
| `GET` `/api/v1/collections/{collection_id}/items`                  | `test_collection_not_found`            | Trả về lỗi `RESOURCE_NOT_FOUND` khi collection cần xem không tồn tại.                                                         |
| `GET` `/api/v1/collections/{collection_id}/items`                  | `test_stranger_cannot_get`             | Trả về lỗi `FORBIDDEN` khi cố lấy danh sách tài liệu từ collection của người dùng khác.                                       |
| `GET` `/api/v1/collections/{collection_id}/items`                  | `test_unauthenticated`                 | Trả về lỗi `UNAUTHORIZED` khi xem danh sách tài liệu trong collection nhưng chưa đăng nhập.                                   |
| `GET` `/api/v1/collections/{collection_id}/items`                  | `test_invalid_pagination_query`        | Trả về lỗi `VALIDATION_ERROR` khi tham số phân trang (page, limit) không hợp lệ (vd: page=0, limit âm, hoặc vượt mức tối đa). |

---

# Test API `/categories`

> Code: [test_categpry_api.py](../tests/api/test_category_api.py)

| Endpoint                   | Tên Test Case  | Kịch bản kiểm thử                                                                                                                 |
|----------------------------|----------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `GET` `/api/v1/categories` | `test_success` | Lấy danh sách các chuyên mục (categories) có sẵn thành công, kiểm tra dữ liệu trả về là một danh sách hợp lệ chứa `id` và `name`. |

---

# Test API `/search`

> Code: [test_search_api.py](../tests/api/test_search_api.py)

---

# Test API `/reports`

> Code: [test_report_api.py](../tests/api/test_report_api.py)

| Endpoint                                         | Tên Test Case                                     | Kịch bản kiểm thử                                                                                        |
|--------------------------------------------------|---------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| `GET` `/api/v1/reports/available_reasons`        | `test_success`                                    | Lấy danh sách các lý do báo cáo (report reasons) khả dụng thành công.                                    |
| <hr>                                             | <hr>                                              | <hr>                                                                                                     |
| `POST` `/api/v1/reports/documents/{document_id}` | `test_user_can_report_others_public_document`     | Gửi báo cáo (report) tài liệu PUBLIC của người dùng khác thành công.                                     |
| `POST` `/api/v1/reports/documents/{document_id}` | `test_user_cannot_report_others_private_document` | Trả về lỗi `FORBIDDEN` khi cố gắng báo cáo tài liệu PRIVATE của người khác.                              |
| `POST` `/api/v1/reports/documents/{document_id}` | `test_unauthenticated`                            | Trả về lỗi `UNAUTHORIZED` khi gửi báo cáo tài liệu nhưng chưa đăng nhập.                                 |
| `POST` `/api/v1/reports/documents/{document_id}` | `test_document_not_found`                         | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu cần báo cáo không tồn tại.                                  |
| `POST` `/api/v1/reports/documents/{document_id}` | `test_invalid_reason`                             | Trả về lỗi `RESOURCE_NOT_FOUND` khi ID của lý do báo cáo (`reason`) truyền lên không tồn tại.            |
| `POST` `/api/v1/reports/documents/{document_id}` | `test_user_already_reported_document`             | Trả về lỗi `ACTION_ALREADY_PERFORMED` khi người dùng báo cáo lại một tài liệu mà họ đã báo cáo trước đó. |

---

# Test API `/users`

> Code: [test_user_api.py](../tests/api/test_user_api.py)

| Endpoint                                   | Tên Test Case              | Kịch bản kiểm thử                                                                                  |
|--------------------------------------------|----------------------------|----------------------------------------------------------------------------------------------------|
| `GET` `/api/v1/users/me/profile`           | `test_success`             | Lấy thông tin cá nhân (profile) thành công, đảm bảo trả về đầy đủ các trường yêu cầu.              |
| `GET` `/api/v1/users/me/profile`           | `test_unauthenticated`     | Trả về lỗi `UNAUTHORIZED` khi lấy thông tin cá nhân nhưng chưa đăng nhập.                          |
| <hr>                                       | <hr>                       | <hr>                                                                                               |
| `PATCH` `/api/v1/users/me/profile`         | `test_success`             | Cập nhật thông tin profile (tên, giới tính, số điện thoại, bio) thành công.                        |
| `PATCH` `/api/v1/users/me/profile`         | `test_unauthenticated`     | Trả về lỗi `UNAUTHORIZED` khi cập nhật profile nhưng chưa đăng nhập.                               |
| `PATCH` `/api/v1/users/me/profile`         | `test_validation_error`    | Trả về lỗi `VALIDATION_ERROR` khi gửi dữ liệu không hợp lệ (ví dụ: sai format giới tính).          |
| <hr>                                       | <hr>                       | <hr>                                                                                               |
| `PUT` `/api/v1/users/me/avatar`            | `test_success`             | Cập nhật ảnh đại diện (avatar) thành công với file hợp lệ.                                         |
| `PUT` `/api/v1/users/me/avatar`            | `test_unauthenticated`     | Trả về lỗi `UNAUTHORIZED` khi upload avatar nhưng chưa đăng nhập.                                  |
| `PUT` `/api/v1/users/me/avatar`            | `test_invalid_avatar_type` | Trả về lỗi `UNSUPPORTED_FILE_TYPE` khi upload định dạng file không được hỗ trợ (.ico, .svg, .pdf). |
| <hr>                                       | <hr>                       | <hr>                                                                                               |
| `GET` `/api/v1/users/me/documents`         | `test_success`             | Lấy danh sách các tài liệu do bản thân upload thành công.                                          |
| `GET` `/api/v1/users/me/documents`         | `test_unauthenticated`     | Trả về lỗi `UNAUTHORIZED` khi cố lấy danh sách tài liệu cá nhân nhưng chưa đăng nhập.              |
| <hr>                                       | <hr>                       | <hr>                                                                                               |
| `GET` `/api/v1/users/me/collections`       | `test_success`             | Lấy danh sách các bộ sưu tập (collections) của bản thân thành công.                                |
| `GET` `/api/v1/users/me/collections`       | `test_unauthenticated`     | Trả về lỗi `UNAUTHORIZED` khi lấy danh sách bộ sưu tập nhưng chưa đăng nhập.                       |
| <hr>                                       | <hr>                       | <hr>                                                                                               |
| `GET` `/api/v1/users/me/liked_documents`   | `test_success`             | Lấy danh sách các tài liệu đã like thành công.                                                     |
| `GET` `/api/v1/users/me/liked_documents`   | `test_unauthenticated`     | Trả về lỗi `UNAUTHORIZED` khi lấy danh sách tài liệu đã like nhưng chưa đăng nhập.                 |
| <hr>                                       | <hr>                       | <hr>                                                                                               |
| `GET` `/api/v1/users/{username}/profile`   | `test_success`             | Xem thông tin công khai (public profile) của một người dùng khác thành công.                       |
| `GET` `/api/v1/users/{username}/profile`   | `test_user_not_found`      | Trả về lỗi `RESOURCE_NOT_FOUND` khi username truyền vào không tồn tại.                             |
| <hr>                                       | <hr>                       | <hr>                                                                                               |
| `GET` `/api/v1/users/{username}/documents` | `test_success`             | Lấy danh sách tài liệu công khai (public) đang hoạt động của người dùng khác thành công.           |
| `GET` `/api/v1/users/{username}/documents` | `test_user_not_found`      | Trả về lỗi `RESOURCE_NOT_FOUND` khi username cần xem tài liệu không tồn tại.                       |

---

# Test API `/admin`

> Code: [test_admin_api.py](../tests/api/test_admin_api.py)

| Endpoint                                               | Tên Test Case                                               | Kịch bản kiểm thử                                                                                                      |
|--------------------------------------------------------|-------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| `ALL` `/api/v1/admin/*`                                | `test_regular_user_forbidden`                               | Trả về lỗi `FORBIDDEN` (với user thường) hoặc `UNAUTHORIZED` (với khách) khi cố truy cập các API dành riêng cho Admin. |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `GET` `/api/v1/admin/users`                            | `test_get_user`                                             | Lấy danh sách người dùng thành công và hỗ trợ các tham số lọc (phân trang, is_active, username, email).                |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `POST` `/api/v1/admin/users/{user_id}/ban`             | `test_ban_user_success`                                     | Khóa (ban) tài khoản người dùng thành công, user bị khóa sẽ nhận lỗi `USER_INACTIVE` khi gọi API.                      |
| `POST` `/api/v1/admin/users/{user_id}/ban`             | `test_ban_unactive_user`                                    | Khóa tài khoản đã bị khóa trước đó thành công (không sinh lỗi khi thao tác lại).                                       |
| `POST` `/api/v1/admin/users/{user_id}/ban`             | `test_ban_user_notfound`                                    | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài khoản cần khóa không tồn tại.                                                  |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `POST` `/api/v1/admin/users/{user_id}/unban`           | `test_unban_user_success`                                   | Mở khóa (unban) tài khoản người dùng thành công, user có thể truy cập lại API bình thường.                             |
| `POST` `/api/v1/admin/users/{user_id}/unban`           | `test_unban_active_user`                                    | Mở khóa tài khoản đang hoạt động bình thường thành công (không sinh lỗi khi thao tác dư thừa).                         |
| `POST` `/api/v1/admin/users/{user_id}/unban`           | `test_unban_user_notfound`                                  | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài khoản cần mở khóa không tồn tại.                                               |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `GET` `/api/v1/admin/documents`                        | `test_list_document`                                        | Admin lấy danh sách tài liệu trong hệ thống thành công (có hỗ trợ phân trang).                                         |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `GET` `/api/v1/admin/documents/{document_id}`          | `test_admin_can_get_public_document`                        | Admin xem chi tiết tài liệu PUBLIC thành công.                                                                         |
| `GET` `/api/v1/admin/documents/{document_id}`          | `test_admin_can_get_private_document`                       | Admin xem chi tiết tài liệu PRIVATE thành công (đặc quyền của admin).                                                  |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `POST` `/api/v1/admin/documents/{document_id}/unban`   | `test_admin_unban_document`                                 | Admin mở khóa tài liệu thành công (chuyển trạng thái từ BANNED sang READY).                                            |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `POST` `/api/v1/admin/categories`                      | `test_create_category`                                      | Admin tạo chuyên mục (category) mới thành công.                                                                        |
| `POST` `/api/v1/admin/categories`                      | `test_create_category_with_existed_name`                    | Trả về lỗi `RESOURCE_ALREADY_EXISTS` khi tên category mới đã tồn tại.                                                  |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `PATCH` `/api/v1/admin/categories/{category_id}`       | `test_rename_category_success`                              | Admin đổi tên chuyên mục (category) thành công.                                                                        |
| `PATCH` `/api/v1/admin/categories/{category_id}`       | `test_rename_category_with_existed_name`                    | Trả về lỗi `RESOURCE_ALREADY_EXISTS` khi đổi sang tên của một category đã có.                                          |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `DELETE` `/api/v1/admin/categories/{category_id}`      | `test_delete_category_success`                              | Admin xóa chuyên mục (category) thành công.                                                                            |
| `DELETE` `/api/v1/admin/categories/{category_id}`      | `test_delete_used_category`                                 | Trả về lỗi `RESOURCE_IN_USE` khi cố xóa category đang chứa tài liệu.                                                   |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `GET` `/api/v1/admin/reports`                          | `test_get_reported_documents`                               | Lấy danh sách các tài liệu đang bị báo cáo (report) thành công.                                                        |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `GET` `/api/v1/admin/reports/documents/{document_id}`  | `test_get_reports_of_document`                              | Lấy danh sách chi tiết các báo cáo của một tài liệu cụ thể thành công.                                                 |
| `GET` `/api/v1/admin/reports/documents/{document_id}`  | `test_get_reported_documents_returns_empty_when_no_reports` | Trả về danh sách rỗng khi lấy báo cáo của tài liệu chưa từng bị report.                                                |
| `GET` `/api/v1/admin/reports/documents/{document_id}`  | `test_get_reports_of_document_document_not_found`           | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu cần lấy danh sách báo cáo không tồn tại.                                  |
| <hr>                                                   | <hr>                                                        | <hr>                                                                                                                   |
| `POST` `/api/v1/admin/reports/documents/{document_id}` | `test_accept_reports_ban_document`                          | Xử lý báo cáo (accept=True), khóa (ban) tài liệu thành công (chuyển sang trạng thái BANNED).                           |
| `POST` `/api/v1/admin/reports/documents/{document_id}` | `test_reject_reports_document_still_accessible`             | Xử lý báo cáo (accept=False), từ chối báo cáo, tài liệu vẫn giữ nguyên trạng thái READY.                               |
| `POST` `/api/v1/admin/reports/documents/{document_id}` | `test_process_reports_document_not_found`                   | Trả về lỗi `RESOURCE_NOT_FOUND` khi tài liệu cần xử lý báo cáo không tồn tại.                                          |