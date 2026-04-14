import { describe, it, expect } from 'vitest'
import { isNull, isNotNull, isEmptyStr, isEmptyObj, deepClone, generateId } from '@/utils/util'

describe('util functions', () => {
  describe('isNull', () => {
    it('should return true for null', () => {
      expect(isNull(null)).toBe(true)
    })

    it('should return true for undefined', () => {
      expect(isNull(undefined)).toBe(true)
    })

    it('should return false for empty string', () => {
      expect(isNull('')).toBe(false)
    })

    it('should return false for zero', () => {
      expect(isNull(0)).toBe(false)
    })

    it('should return false for false', () => {
      expect(isNull(false)).toBe(false)
    })
  })

  describe('isNotNull', () => {
    it('should return false for null', () => {
      expect(isNotNull(null)).toBe(false)
    })

    it('should return true for any value', () => {
      expect(isNotNull('')).toBe(true)
      expect(isNotNull(0)).toBe(true)
      expect(isNotNull(false)).toBe(true)
    })
  })

  describe('isEmptyStr', () => {
    it('should return true for empty string', () => {
      expect(isEmptyStr('')).toBe(true)
    })

    it('should return false for non-empty string', () => {
      expect(isEmptyStr('hello')).toBe(false)
    })

    it('should return true for whitespace only', () => {
      expect(isEmptyStr('   ')).toBe(true)
    })
  })

  describe('isEmptyObj', () => {
    it('should return true for empty object', () => {
      expect(isEmptyObj({})).toBe(true)
    })

    it('should return false for non-empty object', () => {
      expect(isEmptyObj({ a: 1 })).toBe(false)
    })
  })

  describe('deepClone', () => {
    it('should clone primitive values', () => {
      expect(deepClone(1)).toBe(1)
      expect(deepClone('hello')).toBe('hello')
      expect(deepClone(true)).toBe(true)
    })

    it('should clone arrays', () => {
      const original = [1, 2, 3]
      const cloned = deepClone(original)
      expect(cloned).toEqual(original)
      expect(cloned).not.toBe(original)
    })

    it('should clone objects', () => {
      const original = { a: 1, b: { c: 2 } }
      const cloned = deepClone(original)
      expect(cloned).toEqual(original)
      expect(cloned).not.toBe(original)
      expect(cloned.b).not.toBe(original.b)
    })

    it('should handle nested arrays', () => {
      const original = [[1, 2], [3, 4]]
      const cloned = deepClone(original)
      expect(cloned).toEqual(original)
      expect(cloned[0]).not.toBe(original[0])
    })
  })

  describe('generateId', () => {
    it('should generate unique ids', () => {
      const id1 = generateId()
      const id2 = generateId()
      expect(id1).not.toBe(id2)
    })

    it('should return a number', () => {
      expect(typeof generateId()).toBe('number')
    })
  })
})
