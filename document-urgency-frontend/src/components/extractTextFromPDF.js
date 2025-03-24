import * as pdfjsLib from 'pdfjs-dist';


const extractTextFromPDF = async (pdfFile) => {
  const fileReader = new FileReader();
  
  return new Promise((resolve, reject) => {
    // Read the file as ArrayBuffer
    fileReader.onload = async () => {
      const data = new Uint8Array(fileReader.result);
      
      try {
        // Load the PDF document
        const pdf = await pdfjsLib.getDocument(data).promise;
        const numPages = pdf.numPages;
        let fullText = '';
        
        // Loop through all pages
        for (let pageNum = 1; pageNum <= numPages; pageNum++) {
          const page = await pdf.getPage(pageNum);
          const content = await page.getTextContent();
          
          // Extract the text
          const pageText = content.items.map(item => item.str).join(' ');
          fullText += pageText + '\n'; // Add a new line after each page
        }
        
        resolve(fullText);
      } catch (error) {
        reject("Error extracting text: " + error);
      }
    };
    
    fileReader.onerror = () => {
      reject("Error reading the file.");
    };
    
    // Read the PDF file as an ArrayBuffer
    fileReader.readAsArrayBuffer(pdfFile);
  });
};

export default extractTextFromPDF;
