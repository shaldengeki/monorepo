import '@testing-library/jest-dom'
import { jest } from '@jest/globals';
import { TextEncoder, TextDecoder } from 'util';

global.jest = jest;

Object.defineProperty(window, 'TextEncoder', {
  writable: true,
  value: TextEncoder
});

Object.defineProperty(window, 'TextDecoder', {
  writable: true,
  value: TextDecoder
});
