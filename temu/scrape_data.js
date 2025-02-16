function scrapeTemu() {
    let results = [];
    let products = document.querySelectorAll("div.EKDT7a3v");

    products.forEach(product => {
        let titleElem = product.querySelector("div._6q6qVUF5._1QhQr8pq._2gAD5fPC._3AbcHYoU a");
        let priceElem = product.querySelector("div._382YgpSF span._2de9ERAH");
        let soldElem = product.querySelector("span._1GKMA1Nk");
        let ratingElem = product.querySelector("div.WCDudEtm");
        let reviewCountElem = product.querySelector("span._3CizNywp");

        let title = titleElem ? titleElem.innerText.trim() : "N/A";
        let link = titleElem ? "https://www.temu.com" + titleElem.getAttribute("href") : "N/A";
        let price = priceElem ? priceElem.innerText.trim() : "N/A";
        let sold = soldElem ? soldElem.innerText.trim() : "N/A";
        let rating = ratingElem ? ratingElem.getAttribute("aria-label").replace(" score", "").trim() : "N/A";
        let reviews = reviewCountElem ? reviewCountElem.innerText.trim() : "N/A";

        // Chỉ lưu sản phẩm có sold chứa "K"
        if (sold.includes("K")) {
            results.push({ title, link, price, sold, rating, reviews });
        }
    });

    console.table(results);
    return results;
}

function exportToCSV(data, filename = "temu_data.csv") {
    let csvContent = "data:text/csv;charset=utf-8,Title,URL,Price,Sold,Rating,Reviews\n";

    data.forEach(row => {
        csvContent += `"${row.title}","${row.link}","${row.price}","${row.sold}","${row.rating}","${row.reviews}"\n`;
    });

    let encodedUri = encodeURI(csvContent);
    let link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
}

// Gọi hàm này để tải file CSV:
exportToCSV(scrapeTemu());
