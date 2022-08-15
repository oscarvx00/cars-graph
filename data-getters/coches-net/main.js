const { exit } = require('process');
const {
    Builder,
    By,
    Key,
    until
} = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');


let proxyAddress = '20.111.54.16:80'

let option = new chrome.Options()
  .addArguments(`--proxy-server=http://${proxyAddress}`)
  .addArguments("--disable-extensions");
  //.addArguments("--headless");

(async function example() {
    let driver = await new Builder().forBrowser('chrome').setChromeOptions(option).build()
    driver.executeScript("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    try {
        await driver.get('https://www.coches.net/segunda-mano/');
        await driver.sleep(20000)
        await driver.findElement(By.xpath("//button[span[contains(text(), 'Aceptar')]]")).click()
        await driver.sleep(20000)
        //await driver.wait(until.titleIs('webdriver - Google Search'), 1000);
      } catch (err){
        console.error(err)
        exit()
      } 
      finally {
        await driver.quit();
      }
})()