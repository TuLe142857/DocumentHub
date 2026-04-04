/**
 * @template T
 * @typedef {Object} ResponseSuccess
 * @property {true} success
 * @property {T} data
 * @property {string|null} [message]
 */

/**
 * @typedef {Object} ResponseError
 * @property {false} success
 * @property {string} error_code
 * @property {string|null} [message]
 */

/**
 * @typedef {Object} PaginationMeta
 * @property {number} current_page
 * @property {number} per_page
 * @property {number} total_items
 * @property {number} total_pages
 * @property {boolean} has_next
 * @property {boolean} has_prev
 */

/**
 * @template T
 * @typedef {Object} ResponsePagination
 * @property {true} success
 * @property {T[]} data
 * @property {PaginationMeta} meta
 * @property {string|null} [message]
 */

export const Types = {};