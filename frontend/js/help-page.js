document.addEventListener("DOMContentLoaded", async () => {
    const contentDiv = document.getElementById("help-content");
    const btnDownloadPdf = document.getElementById("btn-download-pdf");
    const btnBack = document.getElementById("btn-back");

    // Nazad na prethodnu stranicu
    btnBack.addEventListener("click", () => {
        if (document.referrer) {
            window.history.back();
        } else {
            window.location.href = "/";
        }
    });

    // Učitaj HELP.md sa servera
    try {
        const res = await fetch("/api/v1/help/markdown");
        if (!res.ok) throw new Error("Neuspešno učitavanje uputstva.");
        const markdown = await res.text();

        // Jednostavan Markdown → HTML konverter
        contentDiv.innerHTML = markdownToHtml(markdown);

        // Generiši TOC
        generateToc();
    } catch (e) {
        contentDiv.innerHTML = `<div class="error-state-text">Greška: ${e.message}</div>`;
    }

    // Preuzmi PDF
    btnDownloadPdf.addEventListener("click", async () => {
        btnDownloadPdf.disabled = true;
        btnDownloadPdf.textContent = "⏳...";
        try {
            const res = await fetch("/api/v1/help/pdf", {
                headers: ApiService.getHeaders(),
            });
            if (!res.ok) throw new Error("Greška pri generisanju PDF-a.");
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "ServisMasterOS_Uputstvo.pdf";
            a.click();
            URL.revokeObjectURL(url);
        } catch (e) {
            alert(e.message);
        } finally {
            btnDownloadPdf.disabled = false;
            btnDownloadPdf.textContent = "📥 PDF";
        }
    });

    // ============================================
    // MARKDOWN → HTML (jednostavan konverter)
    // ============================================
    function markdownToHtml(md) {
        let html = md;

        // Code blocks
        html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");

        // Inline code
        html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

        // Headers
        html = html.replace(/^### (.*$)/gim, "<h3>$1</h3>");
        html = html.replace(/^## (.*$)/gim, "<h2>$1</h2>");
        html = html.replace(/^# (.*$)/gim, "<h1>$1</h1>");

        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

        // Italic
        html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");

        // Links
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

        // Horizontal rule
        html = html.replace(/^---$/gim, "<hr>");

        // Lists
        html = html.replace(/^\s*[-*]\s+(.*)$/gim, "<li>$1</li>");
        html = html.replace(/(<li>[\s\S]*?<\/li>)/g, "<ul>$1</ul>");

        // Numbered lists
        html = html.replace(/^\s*\d+\.\s+(.*)$/gim, "<li>$1</li>");

        // Paragraphs (svaki red bez HTML taga)
        html = html.split("\n").map(line => {
            if (line.trim() === "") return "";
            if (line.match(/^<(h[1-6]|ul|ol|li|pre|hr|a|code|strong|em)/)) return line;
            if (line.match(/<\/(ul|ol|pre)>$/)) return line;
            return `<p>${line}</p>`;
        }).join("\n");

        return html;
    }

    function generateToc() {
        // TOC je već u HELP.md, ne treba generisati
    }
});