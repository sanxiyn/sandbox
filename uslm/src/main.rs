use argparse::{ArgumentParser, Store};
use quick_xml::{Error, NsReader};
use quick_xml::events::Event;
use quick_xml::name::{Namespace, ResolveResult};

// See https://uscode.house.gov/download/resources/USLM-User-Guide.pdf
static USLM_NS: &'static [u8] = b"http://xml.house.gov/schemas/uslm/1.0";

fn match_ns(ns: &[u8], resolution: ResolveResult) -> bool {
    match resolution {
        ResolveResult::Bound(Namespace(resolution_ns)) => resolution_ns == ns,
        _ => false
    }
}

fn match_uslm(resolution: ResolveResult) -> bool {
    match_ns(USLM_NS, resolution)
}

macro_rules! check_tag {
    ($expr:expr, $tag:expr) => {
        $expr.as_ref().is_some_and(|x| x.local_name().as_ref() == $tag)
    }
}

macro_rules! get_attribute {
    ($expr:expr, $attribute:expr) => {
        $expr.as_ref().and_then(|x| x.try_get_attribute($attribute).transpose()).transpose()
    }
}

fn print_sections(filename: &str) -> Result<(), Error> {
    let mut reader = NsReader::from_file(filename)?;
    let mut buf = vec![];
    let mut parents = vec![];
    loop {
        let (resolution, event) = reader.read_resolved_event_into(&mut buf)?;
        match event {
            Event::Start(start) => {
                let is_uslm = match_uslm(resolution);
                let parent = is_uslm.then_some(start.to_owned());
                parents.push(parent);
            }
            Event::End(_) => {
                parents.pop();
            }
            Event::Text(text) => {
                if parents.len() < 2 {
                    continue;
                }
                let p1 = &parents[parents.len() - 1];
                if !check_tag!(p1, b"heading") {
                    continue;
                }
                let p2 = &parents[parents.len() - 2];
                if !check_tag!(p2, b"section") {
                    continue;
                }
                let identifier = get_attribute!(p2, b"identifier")?;
                if identifier.is_none() {
                    continue;
                }
                let status = get_attribute!(p2, b"status")?;
                let skip_statuses: &[&[u8]] = &[b"renumbered", b"repealed"];
                if status.is_some_and(|x| skip_statuses.contains(&&*x.value)) {
                    continue;
                }
                let identifier = identifier.unwrap().unescape_value()?;
                let text = text.unescape()?;
                println!("{} {}", identifier, text.trim());
            }
            Event::Eof => break,
            _ => ()
        }
    }
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut filename = String::new();
    {
        let mut parser = ArgumentParser::new();
        parser.refer(&mut filename).add_argument("filename", Store, "");
        parser.parse_args_or_exit();
    }
    print_sections(&filename)?;
    Ok(())
}
