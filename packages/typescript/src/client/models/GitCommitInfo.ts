/* tslint:disable */
/* eslint-disable */
/**
 * Daytona Server API
 * Daytona Server API
 *
 * The version of the OpenAPI document: v0.0.0-dev
 *
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { mapValues } from '../runtime'
/**
 *
 * @export
 * @interface GitCommitInfo
 */
export interface GitCommitInfo {
  /**
   *
   * @type {string}
   * @memberof GitCommitInfo
   */
  author: string
  /**
   *
   * @type {string}
   * @memberof GitCommitInfo
   */
  email: string
  /**
   *
   * @type {string}
   * @memberof GitCommitInfo
   */
  hash: string
  /**
   *
   * @type {string}
   * @memberof GitCommitInfo
   */
  message: string
  /**
   *
   * @type {string}
   * @memberof GitCommitInfo
   */
  timestamp: string
}

/**
 * Check if a given object implements the GitCommitInfo interface.
 */
export function instanceOfGitCommitInfo(value: object): value is GitCommitInfo {
  if (!('author' in value) || value['author'] === undefined) return false
  if (!('email' in value) || value['email'] === undefined) return false
  if (!('hash' in value) || value['hash'] === undefined) return false
  if (!('message' in value) || value['message'] === undefined) return false
  if (!('timestamp' in value) || value['timestamp'] === undefined) return false
  return true
}

export function GitCommitInfoFromJSON(json: any): GitCommitInfo {
  return GitCommitInfoFromJSONTyped(json, false)
}

export function GitCommitInfoFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean,
): GitCommitInfo {
  if (json == null) {
    return json
  }
  return {
    author: json['author'],
    email: json['email'],
    hash: json['hash'],
    message: json['message'],
    timestamp: json['timestamp'],
  }
}

export function GitCommitInfoToJSON(json: any): GitCommitInfo {
  return GitCommitInfoToJSONTyped(json, false)
}

export function GitCommitInfoToJSONTyped(
  value?: GitCommitInfo | null,
  ignoreDiscriminator: boolean = false,
): any {
  if (value == null) {
    return value
  }

  return {
    author: value['author'],
    email: value['email'],
    hash: value['hash'],
    message: value['message'],
    timestamp: value['timestamp'],
  }
}