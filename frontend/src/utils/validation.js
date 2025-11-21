/**
 * Validation utilities for form inputs
 */

/**
 * Validate name
 * @param {string} name - Name to validate
 * @returns {object} { valid: boolean, error: string }
 */
export function validateName(name) {
  if (!name || name.trim().length === 0) {
    return { valid: false, error: "Name is required" };
  }
  if (name.trim().length < 1) {
    return { valid: false, error: "Name must be at least 1 character" };
  }
  if (name.length > 100) {
    return { valid: false, error: "Name must be less than 100 characters" };
  }
  return { valid: true, error: null };
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {object} { valid: boolean, error: string }
 */
export function validateEmail(email) {
  if (!email || email.trim().length === 0) {
    return { valid: false, error: "Email is required" };
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, error: "Please enter a valid email address" };
  }
  return { valid: true, error: null };
}

/**
 * Validate timezone
 * @param {string} timezone - Timezone to validate
 * @returns {object} { valid: boolean, error: string }
 */
export function validateTimezone(timezone) {
  if (!timezone || timezone.trim().length === 0) {
    return { valid: false, error: "Timezone is required" };
  }
  // Basic validation - check if it's a valid timezone string format
  // More comprehensive validation would check against IANA timezone database
  if (timezone.length < 3 || timezone.length > 50) {
    return { valid: false, error: "Please select a valid timezone" };
  }
  return { valid: true, error: null };
}

/**
 * Validate goals text
 * @param {string} goals - Goals text to validate
 * @returns {object} { valid: boolean, error: string }
 */
export function validateGoals(goals) {
  if (!goals || goals.trim().length === 0) {
    return { valid: false, error: "Goals are required" };
  }
  if (goals.trim().length < 10) {
    return { valid: false, error: "Please provide more details (at least 10 characters)" };
  }
  if (goals.length > 1000) {
    return { valid: false, error: "Goals must be less than 1000 characters" };
  }
  return { valid: true, error: null };
}

