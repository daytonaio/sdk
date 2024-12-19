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
import type { Project } from './Project'
import {
  ProjectFromJSON,
  ProjectFromJSONTyped,
  ProjectToJSON,
  ProjectToJSONTyped,
} from './Project'
import type { WorkspaceInfo } from './WorkspaceInfo'
import {
  WorkspaceInfoFromJSON,
  WorkspaceInfoFromJSONTyped,
  WorkspaceInfoToJSON,
  WorkspaceInfoToJSONTyped,
} from './WorkspaceInfo'

/**
 *
 * @export
 * @interface WorkspaceDTO
 */
export interface WorkspaceDTO {
  /**
   *
   * @type {string}
   * @memberof WorkspaceDTO
   */
  id: string
  /**
   *
   * @type {WorkspaceInfo}
   * @memberof WorkspaceDTO
   */
  info?: WorkspaceInfo
  /**
   *
   * @type {string}
   * @memberof WorkspaceDTO
   */
  name: string
  /**
   *
   * @type {Array<Project>}
   * @memberof WorkspaceDTO
   */
  projects: Array<Project>
  /**
   *
   * @type {string}
   * @memberof WorkspaceDTO
   */
  target: string
}

/**
 * Check if a given object implements the WorkspaceDTO interface.
 */
export function instanceOfWorkspaceDTO(value: object): value is WorkspaceDTO {
  if (!('id' in value) || value['id'] === undefined) return false
  if (!('name' in value) || value['name'] === undefined) return false
  if (!('projects' in value) || value['projects'] === undefined) return false
  if (!('target' in value) || value['target'] === undefined) return false
  return true
}

export function WorkspaceDTOFromJSON(json: any): WorkspaceDTO {
  return WorkspaceDTOFromJSONTyped(json, false)
}

export function WorkspaceDTOFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean,
): WorkspaceDTO {
  if (json == null) {
    return json
  }
  return {
    id: json['id'],
    info:
      json['info'] == null ? undefined : WorkspaceInfoFromJSON(json['info']),
    name: json['name'],
    projects: (json['projects'] as Array<any>).map(ProjectFromJSON),
    target: json['target'],
  }
}

export function WorkspaceDTOToJSON(json: any): WorkspaceDTO {
  return WorkspaceDTOToJSONTyped(json, false)
}

export function WorkspaceDTOToJSONTyped(
  value?: WorkspaceDTO | null,
  ignoreDiscriminator: boolean = false,
): any {
  if (value == null) {
    return value
  }

  return {
    id: value['id'],
    info: WorkspaceInfoToJSON(value['info']),
    name: value['name'],
    projects: (value['projects'] as Array<any>).map(ProjectToJSON),
    target: value['target'],
  }
}