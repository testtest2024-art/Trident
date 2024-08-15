from typing import List

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver

from agent.model.step import Element


class AndroidWebViewDriver(WebDriver):
    def __init__(
        self, options: Options = None, service: Service = None, keep_alive: bool = True
    ):
        """

        :param device:    AdbDevice
        :param version:   chrome
        """
        super().__init__(options, service, keep_alive)

    def hierarchy_to_element(self) -> List[Element]:
        """
        Android H5
        :return:
        """

        js = """
            function getXpath(element) {
                if (element.id!=='')
                    return `id('${element.id}')`;
                if (element===document.body)
                    return element.tagName;
            
                let ix= 0;
                let siblings= element.parentNode.childNodes;
                for (let i= 0; i<siblings.length; i++) {
                    let sibling= siblings[i];
                    if (sibling===element)
                        return getXpath(element.parentNode)+'/'+element.tagName.toLowerCase()+'['+(ix+1)+']';
                    if (sibling.nodeType===1 && sibling.tagName===element.tagName)
                        ix++;
                }
            
                return getXpath(element)
            }
            
            function getElementText(element) {
              var text = "";
              var childNodes = element.childNodes;
              for (var i = 0; i < childNodes.length; i++) {
                var node = childNodes[i];
                if (node.nodeType === Node.TEXT_NODE) {
                  text += node.textContent;
                }
              }
              return text;
            }
            
            let result = []
            let elements = document.body.getElementsByTagName("*")
            for (let i=0; i<elements.length; i++) {
              let element = elements[i]
              let clickable = false
              let canInput = false
              let elementText = getElementText(element)
              let position = element.getBoundingClientRect()
              
              if (element.tagName === "A" || getEventListeners(element).click !== undefined) {
                clickable = true
              }
              
              if (element.tagName === "INPUT") {
                canInput = true
              }
              
              if (clickable || canInput || elementText) {
                  result.push({
                    text: elementText,
                    xpath: getXpath(element),
                    clickable: clickable,
                    can_input: canInput,
                    x: position.x,
                    y: position.y,
                    width: position.width,
                    height: position.height
                  })
              }
            }
        """

        self.execute_cdp_cmd(
            "Runtime.evaluate",
            {
                "expression": js,
                "includeCommandLineAPI": True,
            },
        )

        result: List = self.execute_script("return result")

        virtual_element_list = [Element(**r) for r in result]

        print(virtual_element_list)

        return virtual_element_list
