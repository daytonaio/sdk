/**
 * Custom error class for timeout-related exceptions
 * @extends Error
 */
export class TimeoutError extends Error {
  constructor(message: string = "Operation timed out") {
    super(message);
    this.name = "TimeoutError";
    this.message = message;
    Object.setPrototypeOf(this, TimeoutError.prototype);
  }
}