export function breakIntoSentences(text) {
    text = text.replace("U.S.", "US");
    return text.match(/[^.!?]+[.!?]+/g) || [];
}
  
export function formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString("en-GB", {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
    });
}