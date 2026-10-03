const generateCibilScore = (pan) => {
    let hash = 0;
    for (let i = 0; i < pan.length; i++) {
        const char = pan.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    // Normalize to 300-900 range
    const score = (Math.abs(hash) % 600) + 300;
    return score;
};

const findPans = () => {
    const targets = {
        "Low (< 500)": [],
        "Medium (600-700)": [],
        "High (> 750)": []
    };

    const prefixes = ["ABCDE", "FGHIJ", "KLMNO"];
    const suffixes = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    let count = 0;
    while ((targets["Low (< 500)"].length < 3 || targets["Medium (600-700)"].length < 3 || targets["High (> 750)"].length < 3) && count < 1000000) {
        const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
        const digits = Math.floor(Math.random() * 9000) + 1000;
        const suffix = suffixes[Math.floor(Math.random() * suffixes.length)];
        const pan = `${prefix}${digits}${suffix}`;

        const score = generateCibilScore(pan);

        if (score < 500 && targets["Low (< 500)"].length < 3) {
            targets["Low (< 500)"].push({ pan, score });
        } else if (score >= 600 && score < 700 && targets["Medium (600-700)"].length < 3) {
            targets["Medium (600-700)"].push({ pan, score });
        } else if (score > 750 && targets["High (> 750)"].length < 3) {
            targets["High (> 750)"].push({ pan, score });
        }
        count++;
    }

    const fs = require('fs');
    const path = require('path');
    let output = "------------------------------\n";
    for (const [category, items] of Object.entries(targets)) {
        output += `${category}:\n`;
        items.forEach(item => output += `  PAN: ${item.pan} | Score: ${item.score}\n`);
    }
    output += "------------------------------\n";
    const outputPath = path.join(__dirname, '..', 'pans_js.txt');
    fs.writeFileSync(outputPath, output);
    console.log("Done writing to pans_js.txt");
};

findPans();
