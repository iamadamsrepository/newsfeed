export function formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString("en-GB", {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
    });
}