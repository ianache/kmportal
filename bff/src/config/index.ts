import dotenv from 'dotenv';

dotenv.config();

interface Config {
  nodeEnv: string;
  port: number;
  apiUrl: string;
  redisUrl: string;
  keycloak: {
    url: string;
    realm: string;
    clientId: string;
    clientSecret: string;
  };
  session: {
    secret: string;
    maxAge: number;
  };
  corsOrigins: string[];
  cookie: {
    domain: string;
    secure: boolean;
  };
  logLevel: string;
}

function getEnvVar(name: string, required: boolean = true, defaultValue?: string): string {
  const value = process.env[name] || defaultValue;
  if (required && !value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value || '';
}

function getEnvVarAsNumber(name: string, required: boolean = true, defaultValue?: number): number {
  const value = process.env[name];
  if (!value) {
    if (required && defaultValue === undefined) {
      throw new Error(`Missing required environment variable: ${name}`);
    }
    return defaultValue || 0;
  }
  const num = parseInt(value, 10);
  if (isNaN(num)) {
    throw new Error(`Environment variable ${name} must be a number`);
  }
  return num;
}

function getEnvVarAsArray(name: string, delimiter: string = ','): string[] {
  const value = process.env[name];
  if (!value) return [];
  return value.split(delimiter).map(s => s.trim()).filter(Boolean);
}

function getEnvVarAsBoolean(name: string, defaultValue: boolean = false): boolean {
  const value = process.env[name];
  if (!value) return defaultValue;
  return value.toLowerCase() === 'true' || value === '1';
}

export const config: Config = {
  nodeEnv: getEnvVar('NODE_ENV', false, 'development'),
  port: getEnvVarAsNumber('PORT', false, 3000),
  apiUrl: getEnvVar('API_URL', false, 'http://api:8000'),
  redisUrl: getEnvVar('REDIS_URL', false, 'redis://redis:6379'),
  keycloak: {
    url: getEnvVar('KEYCLOAK_URL', true),
    realm: getEnvVar('KEYCLOAK_REALM', true),
    clientId: getEnvVar('KEYCLOAK_CLIENT_ID', true),
    clientSecret: getEnvVar('KEYCLOAK_CLIENT_SECRET', true),
  },
  session: {
    secret: getEnvVar('SESSION_SECRET', true),
    maxAge: getEnvVarAsNumber('SESSION_MAX_AGE', false, 7 * 24 * 60 * 60 * 1000), // 7 days
  },
  corsOrigins: getEnvVarAsArray('CORS_ORIGINS'),
  cookie: {
    domain: getEnvVar('COOKIE_DOMAIN', false, 'localhost'),
    secure: getEnvVarAsBoolean('COOKIE_SECURE', false),
  },
  logLevel: getEnvVar('LOG_LEVEL', false, 'info'),
};

export default config;
