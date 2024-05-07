const table = document.querySelector("table")


reasonIndex = -1
envelopeIndex = -1

elements = Array.from(table.querySelectorAll("tr"))
spans = Array.from(table.querySelectorAll("tr td>span"))

elements.forEach((element, ind) => {
    if (element.textContent.includes("Reason") && ind > 0) {
        reasonIndex = ind
    }
});

spans.forEach((element, ind) => {
    if (element.textContent.includes("<Envelope") && envelopeIndex == -1) {
        envelopeIndex = ind
    }
});

// console.log(spans);
// console.log(envelopeIndex)
const elementsToHighlight = elements.slice(reasonIndex)

const xmlELements = elements.slice(envelopeIndex, reasonIndex).filter(element => element.innerText.includes("<Envelope"))

const beforeTd = xmlELements[0]?.querySelectorAll("td")[1];
const afterTd = xmlELements[1]?.querySelectorAll("td")[2];

const dataXmlElements = [beforeTd,afterTd]

const xmls = dataXmlElements.filter(ele =>  ele.querySelectorAll("td span"))

console.log(xmls);

xmls.forEach((span, ind) => ind === 0 ? span.classList.add("xmlBefore") : span.classList.add("xmlAfter"))

let xmlBefore = xmls[0].innerText
let xmlAfter = xmls[1].innerText

elementsAfter = []
elementsBefore = []

elementsToHighlight.forEach(ele => {
    if (ele) {
        try {

            if(ele.querySelector("td[class*='jrcel cel_afterXmlPath']").innerText)
                elementsAfter.push({
                    element: ele.querySelector("td[class*='jrcel cel_afterXmlPath']").innerText.includes("@") ? 
                    ele.querySelector("td[class*='jrcel cel_afterXmlPath']").innerText.substring(
                        0,ele.querySelector("td[class*='jrcel cel_afterXmlPath']").innerText.indexOf("@")
                    )+"text()" : ele.querySelector("td[class*='jrcel cel_afterXmlPath']").innerText,
                    value: ele.querySelector("td[class*='jrcel cel_afterNodeValue']").innerText
                });

            if(ele.querySelector("td[class*='jrcel cel_beforeXmlPath']").innerText)
                elementsBefore.push({
                    element: ele.querySelector("td[class*='jrcel cel_beforeXmlPath']").innerText.includes("@") ? 
                    ele.querySelector("td[class*='jrcel cel_beforeXmlPath']").innerText.substring(
                        0,ele.querySelector("td[class*='jrcel cel_beforeXmlPath']").innerText.indexOf("@")
                    )+"text()" : ele.querySelector("td[class*='jrcel cel_beforeXmlPath']").innerText,
                    value: ele.querySelector("td[class*='jrcel cel_beforeNodeValue']").innerText
                });
        } catch (e) {
            //pass this to remove unwanted elements
        }
    }
})


const wrapXmlInSpan = (xml,leftOrRight)=>{
    const splittedXml = xml.split("\n")

    const newXml = []
   splittedXml.forEach(line => {
        formattedLine = line.replaceAll("</","#LT##SLASH#").replaceAll(">","#GT#").replaceAll("<","#LT#")

        let newLine = formattedLine.split("#")[0];
        formattedLine = formattedLine.trim()

        const actualContentWithTag = formattedLine.split("T#")[1].split("#G")[0]
        const splittedContent = actualContentWithTag.split(" ")
        let tagName = actualContentWithTag
        let actualContent = ""

        
            

        if(splittedContent.length>1){
                tagName = splittedContent[0]
                actualContent = splittedContent.slice(1).join(" ")
        }

        if(!formattedLine.includes(`#SLASH#`)){
            newLine += `<span class="${leftOrRight}-${tagName}">&lt;${tagName}&gt;${actualContent}`


        }else if(formattedLine.includes(`#SLASH#`)){

            

            if(formattedLine.includes(`#LT#${tagName.replace("#SLASH#")}#GT`)){

                newLine += `<span class="${leftOrRight}-${tagName}">`
                newLine += formattedLine.replaceAll("#LT#","&lt;").replaceAll("#GT#","&gt;").replaceAll("#SLASH#","/") + "</span>"
            }else if(formattedLine.includes(`Ccy=`)){

              
                newLine += `<span class="${leftOrRight}-${tagName}">`
                newLine += formattedLine.replaceAll("#LT#","&lt;").replaceAll("#GT#","&gt;").replaceAll("#SLASH#","/") + "</span>"
            
            }
            else{
                newLine += formattedLine.replaceAll("#LT#","&lt;").replaceAll("#GT#","&gt;").replaceAll("#SLASH#","/")
            newLine += "</span>"
            }

            

            newLine = newLine.replaceAll("#SLASH#","")

        }

        newXml.push(newLine)
   });

   return newXml.join("\n")
}
xmlBefore = wrapXmlInSpan(xmlBefore,"left") 
xmlAfter = wrapXmlInSpan(xmlAfter,"right") 


document.querySelector(".xmlBefore").innerHTML = `<pre>${xmlBefore}</pre>`;
document.querySelector(".xmlAfter").innerHTML = `<pre>${xmlAfter}</pre>`;

const injectDiff = (elements,leftOrRight)=>{
    elements.forEach( ({element,_}) => {

        
        const query = element
        .split("/")
        .slice(1,-2)
        .join("/")
        .replaceAll("[","")
        .replaceAll("]","")
        .split("/")
        .map(ele => ele.substring(0,ele.length-1))
        .join(" ." + leftOrRight+"-")
    
        try {
            
        const alteredElement = !element.includes("text") ? element+"/text()" : element

        const tag= alteredElement.split("/")[alteredElement.split("/").length-2].split("[")[0]

        let finalQuery = ""
        if(tag.includes("@")){

            finalQuery = `.${leftOrRight}-${query}`

        }else finalQuery = `.${leftOrRight}-${query} .${leftOrRight}-${tag}`
        const eles = document.querySelectorAll(finalQuery);

        console.log("----------------------");
        console.log(finalQuery);
      
        const lastChar = element.split("/")[element.split("/").length-2].split("[")


        const nthChild = lastChar[1][0]

        

        if(eles[nthChild-1])
            eles[nthChild-1].classList.add("diffactual")//.backgroundColor="yellow"

        } catch (error) {
            console.log("this");
        }
    })
}

console.log(elementsBefore);
injectDiff(elementsBefore,"left")
injectDiff(elementsAfter,"right")



