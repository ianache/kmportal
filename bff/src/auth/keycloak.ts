import { Issuer, Client } from 'openid-client';
import { config } from '../config';

let keycloakClient: Client | null = null;

export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  idToken?: string;
  expiresAt: number;
  userInfo: {
    sub: string;
    email: string;
    roles: string[];
  };
}

/**
 * Decode a JWT payload without re-verifying the signature.
 * Safe to use here because the token was received directly from Keycloak
 * via a server-to-server grant call.
 */
function decodeJwtPayload(token: string): Record<string, any> {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(Buffer.from(base64, 'base64').toString('utf-8'));
  } catch {
    return {};
  }
}

/**
 * Extract application roles from the Keycloak access token.
 * Merges realm-level roles with client-level roles.
 */
function extractRoles(accessToken: string, clientId: string): string[] {
  const payload = decodeJwtPayload(accessToken);
  const realmRoles: string[] = payload?.realm_access?.roles ?? [];
  const clientRoles: string[] = payload?.resource_access?.[clientId]?.roles ?? [];
  return [...new Set([...realmRoles, ...clientRoles])];
}

export async function initializeKeycloakClient(): Promise<Client> {
  if (keycloakClient) {
    return keycloakClient;
  }

  const issuerUrl = `${config.keycloak.url}/realms/${config.keycloak.realm}`;
  
  try {
    const issuer = await Issuer.discover(issuerUrl);
    
    keycloakClient = new issuer.Client({
      client_id: config.keycloak.clientId,
      client_secret: config.keycloak.clientSecret,
      redirect_uris: [`http://localhost:${config.port}/auth/callback`],
      response_types: ['code'],
    });

    console.log('Keycloak client initialized successfully');
    return keycloakClient;
  } catch (error) {
    console.error('Failed to initialize Keycloak client:', error);
    throw new Error('Keycloak initialization failed');
  }
}

export async function exchangeCodeForTokens(code: string): Promise<TokenResponse> {
  const client = await initializeKeycloakClient();

  try {
    const tokenSet = await client.grant({
      grant_type: 'authorization_code',
      code,
      redirect_uri: `http://localhost:${config.port}/auth/callback`,
    });

    const idClaims = tokenSet.claims();
    const accessToken = tokenSet.access_token || '';

    return {
      accessToken,
      refreshToken: tokenSet.refresh_token || '',
      idToken: tokenSet.id_token,
      expiresAt: tokenSet.expires_at || Date.now() + 300000,
      userInfo: {
        sub: idClaims.sub ?? '',
        email: (idClaims.email as string) ?? '',
        roles: extractRoles(accessToken, config.keycloak.clientId),
      },
    };
  } catch (error) {
    console.error('Token exchange failed:', error);
    throw new Error('Failed to exchange authorization code for tokens');
  }
}

export async function refreshAccessToken(refreshToken: string): Promise<TokenResponse> {
  const client = await initializeKeycloakClient();
  
  try {
    const tokenSet = await client.refresh(refreshToken);

    return {
      accessToken: tokenSet.access_token || '',
      refreshToken: tokenSet.refresh_token || refreshToken,
      idToken: tokenSet.id_token,
      expiresAt: tokenSet.expires_at || Date.now() + 300000,
    };
  } catch (error) {
    console.error('Token refresh failed:', error);
    throw new Error('Failed to refresh access token');
  }
}

export function getKeycloakClient(): Client {
  if (!keycloakClient) {
    throw new Error('Keycloak client not initialized');
  }
  return keycloakClient;
}

export { keycloakClient };
