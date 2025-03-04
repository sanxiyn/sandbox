use clap::{App, Arg};
use select::document::Document;
use select::predicate::{Class, Name};
use url::Url;

const URL: &str = "https://lobste.rs/search";

fn search(topic: &str) {
    let query = if topic.contains(" ") {
        format!("\"{}\"", topic)
    } else {
        topic.to_string()
    };
    let params = [("what", "stories"), ("order", "newest"), ("q", &query)];
    let url = Url::parse_with_params(URL, params).unwrap();
    let response = reqwest::blocking::get(url).unwrap();
    let html = Document::from_read(response).unwrap();
    let count = html.find(Class("heading")).next().unwrap().text();
    let count = count.trim();
    let count = count.split_whitespace().take(2).collect::<Vec<_>>().join(" ");
    println!("{}", count);
    let selection = html.find(Class("link")).into_selection();
    let selection = selection.find(Name("a"));
    for item in selection.iter() {
        let text = item.text();
        println!(" * {}", text);
    }
}

fn main() {
    let matches = App::new("lobsters-search")
        .arg(Arg::with_name("topic").required(true).multiple(true))
        .get_matches();
    let topic = matches.values_of("topic").unwrap();
    let topic = topic.collect::<Vec<_>>().join(" ");
    search(&topic);
}
