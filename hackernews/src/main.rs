use std::error::Error;
use std::fs::File;
use std::io::Write;

use clap::{App, Arg};
use futures::stream::FuturesUnordered;
use indicatif::ProgressIterator;
use reqwest::Client;
use serde_json::Value;

// https://github.com/HackerNews/API
const API_URL: &str = "https://hacker-news.firebaseio.com/v0";

async fn get_item(client: &Client, item: i64) -> reqwest::Result<Value> {
    let url = format!("{}/item/{}.json", API_URL, item);
    let response = client.get(&url).send().await?;
    let item = response.json().await?;
    Ok(item)
}

async fn get_items(client: &Client, user: &str) -> reqwest::Result<Vec<i64>> {
    let url = format!("{}/user/{}.json", API_URL, user);
    let response = client.get(&url).send().await?;
    let user: Value = response.json().await?;
    let submitted = user["submitted"].as_array().unwrap();
    let items = submitted.iter().map(|v| v.as_i64().unwrap()).collect();
    Ok(items)
}

async fn run(user: &str) -> Result<(), Box<dyn Error>> {
    let mut file = File::create("items.json")?;
    let client = Client::new();
    let items = get_items(&client, user).await?;
    let count = items.len() as u64;
    let aws = items.into_iter().map(|item| Box::pin(get_item(&client, item)));
    let aws_as_completed = aws.collect::<FuturesUnordered<_>>();
    let progress = aws_as_completed.into_iter().progress_count(count);
    for aw in progress {
        let item = aw.await?;
        if item["type"].as_str().unwrap() != "comment" {
            continue;
        }
        let s = serde_json::to_string(&item)?;
        writeln!(file, "{}", s)?;
    }
    Ok(())
}

#[tokio::main]
async fn main() {
    let matches = App::new("hn-downloader")
        .arg(Arg::with_name("user").required(true).value_name("ID"))
        .get_matches();
    let user = matches.value_of("user").unwrap();
    match run(user).await {
        Ok(_) => (),
        Err(e) => {
            eprintln!("Error: {}", e.to_string());
        }
    }
}
