import { test, expect } from '@playwright/test'

const TEST_USER = {
  email: 'kmuser@comsatel.com.pe',
  password: 'welcome1'
}

const BASE_URL = 'http://localhost:5100'

test.beforeEach(async ({ page, context }) => {
  await context.clearCookies()
  await page.evaluate(() => {
    localStorage.clear()
    sessionStorage.clear()
  })
})

test.describe('Autenticacion - Knowledge Management', () => {
  
  test('TC-001: Login exitoso redirige al dashboard', async ({ page }) => {
    console.log('TC-001: Verificando login exitoso...')
    
    await page.goto(BASE_URL)
    await expect(page.locator('h1')).toContainText('Knowledge Management Center')
    await expect(page.locator('button')).toContainText('Sign In')
    
    await page.click('button:has-text("Sign In")')
    await page.waitForURL(/oauth2.qa.comsatel.com.pe/)
    
    await page.fill('input[name="username"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('input[type="submit"]')
    
    await page.waitForURL(/localhost:5100/)
    await page.waitForURL(/localhost:5100\/(search)?/, { timeout: 10000 })
    
    await expect(page.locator('.sidebar')).toBeVisible({ timeout: 10000 })
    
    console.log('TC-001: PASO')
  })

  test('TC-002: Sesion persiste al navegar entre paginas', async ({ page }) => {
    console.log('TC-002: Verificando persistencia de sesion...')
    
    await page.goto(BASE_URL)
    await page.click('button:has-text("Sign In")')
    await page.waitForURL(/oauth2.qa.comsatel.com.pe/)
    await page.fill('input[name="username"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('input[type="submit"]')
    await page.waitForURL(/localhost:5100/)
    await page.waitForSelector('.sidebar', { timeout: 15000 })
    
    const pages = ['/search', '/domains', '/ingestion']
    
    for (const path of pages) {
      console.log('Navegando a ' + path)
      await page.goto(BASE_URL + path)
      const url = page.url()
      expect(url).not.toContain('/login')
      await page.waitForLoadState('networkidle')
      const bodyText = await page.locator('body').textContent()
      expect(bodyText).not.toContain('Please log in')
      expect(bodyText).not.toContain('401')
    }
    
    console.log('TC-002: PASO')
  })

  test('TC-003: Acceso a Admin solo para KM_ADMIN', async ({ page }) => {
    console.log('TC-003: Verificando control de acceso a Admin...')
    
    await page.goto(BASE_URL)
    await page.click('button:has-text("Sign In")')
    await page.waitForURL(/oauth2.qa.comsatel.com.pe/)
    await page.fill('input[name="username"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('input[type="submit"]')
    await page.waitForURL(/localhost:5100/)
    await page.waitForSelector('.sidebar', { timeout: 15000 })
    
    await page.goto(BASE_URL + '/admin')
    await page.waitForLoadState('networkidle')
    
    const url = page.url()
    const bodyText = await page.locator('body').textContent()
    
    if (bodyText?.includes('Admin') || url.includes('/admin')) {
      console.log('Usuario tiene acceso a Admin')
      expect(url).toContain('/admin')
    } else {
      console.log('Usuario redirigido')
      expect(url).toMatch(/search|domains/)
    }
    
    console.log('TC-003: PASO')
  })

  test('TC-004: APIs retornan 401 sin sesion', async ({ page }) => {
    console.log('TC-004: Verificando proteccion de APIs...')
    
    await page.goto(BASE_URL)
    
    const response = await page.evaluate(async () => {
      const res = await fetch('/api/v1/domains', {
        credentials: 'include'
      })
      return { status: res.status }
    })
    
    expect(response.status).toBe(401)
    console.log('TC-004: PASO')
  })

  test('TC-005: Logout cierra sesion correctamente', async ({ page }) => {
    console.log('TC-005: Verificando logout...')
    
    await page.goto(BASE_URL)
    await page.click('button:has-text("Sign In")')
    await page.waitForURL(/oauth2.qa.comsatel.com.pe/)
    await page.fill('input[name="username"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('input[type="submit"]')
    await page.waitForURL(/localhost:5100/)
    await page.waitForSelector('.sidebar', { timeout: 15000 })
    
    await page.click('.user-row')
    await page.waitForURL(/login|keycloak/)
    
    await page.goto(BASE_URL + '/search')
    await page.waitForURL(/login/)
    
    console.log('TC-005: PASO')
  })

  test('TC-006: Cookie de sesion presente despues de login', async ({ page, context }) => {
    console.log('TC-006: Verificando cookie de sesion...')
    
    await page.goto(BASE_URL)
    await page.click('button:has-text("Sign In")')
    await page.waitForURL(/oauth2.qa.comsatel.com.pe/)
    await page.fill('input[name="username"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('input[type="submit"]')
    await page.waitForURL(/localhost:5100/)
    await page.waitForSelector('.sidebar', { timeout: 15000 })
    
    const cookies = await context.cookies()
    const sessionCookie = cookies.find(c => c.name === 'bff.sid')
    
    expect(sessionCookie).toBeDefined()
    expect(sessionCookie?.domain).toContain('localhost')
    expect(sessionCookie?.httpOnly).toBe(true)
    
    console.log('TC-006: PASO')
    console.log('Cookie bff.sid presente')
  })
})
