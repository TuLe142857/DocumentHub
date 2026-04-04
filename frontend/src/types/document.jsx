/**
 * @typedef {Object} Document
 * @property {number} id
 * @property {string} title
 * @property {"PUBLIC"|"PRIVATE"} visibility
 * @property {"PROCESSING"|"COMPLETED"|"FAILED"} status
 * @property {string} owner
 * @property {string} file_thumbnail_url
 * @property {number} view_count
 * @property {number} download_count
 * @property {string} category
 * @property {string[]} tags
 * @property {string} file_type
 */

/**
 * @typedef {Object} DocumentDetail
 * @property {number} id
 * @property {string} title
 * @property {"PUBLIC"|"PRIVATE"} visibility
 * @property {"PROCESSING"|"COMPLETED"|"FAILED"} status
 * @property {string} owner
 * @property {string} file_thumbnail_url
 * @property {number} view_count
 * @property {number} download_count
 * @property {string} category
 * @property {string[]} tags
 * @property {string} file_type
 * @property {string} desc
 * @property {string} file_original_url
 * @property {string} file_preview_url
 * @property {string} sha256sum
 * @property {string} md5sum
 * @property {number} page_count
 * @property {number} like_count
 */

export const Types = {};