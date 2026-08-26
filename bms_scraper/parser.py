"""
BookMyShow HTML & JSON State Parser.
Parses raw HTML from BookMyShow pages and extracts clean, structured data objects.
"""

import json
import re
from typing import List, Dict, Any, Optional
from urllib.parse import unquote

from .models import (
    City,
    MovieSummary,
    EventSummary,
    CastMember,
    MovieDetailsResponse,
    ShowtimeItem,
    CinemaVenueShowtimes,
    VenueDetailsResponse,
)
from .config import CONFIG



class BMSParser:

    @staticmethod
    def extract_initial_state(html: str) -> Optional[Dict[str, Any]]:
        """Extracts and parses window.__INITIAL_STATE__ JSON object from HTML string."""
        if not html:
            return None

        # Look for window.__INITIAL_STATE__ =
        target_keys = ["window.__INITIAL_STATE__ =", "window.__INITIAL_STATE__="]
        idx = -1
        for key in target_keys:
            idx = html.find(key)
            if idx != -1:
                idx += len(key)
                break

        if idx == -1:
            # Fallback search for script content
            matches = re.findall(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
            if matches:
                try:
                    return json.loads(matches[0])
                except Exception:
                    pass
            return None

        start_idx = html.find("{", idx)
        if start_idx == -1:
            return None

        try:
            decoder = json.JSONDecoder()
            data, _ = decoder.raw_decode(html[start_idx:])
            return data
        except Exception:
            # Secondary regex fallback
            try:
                sub = html[start_idx:start_idx + 500000]
                end_script = sub.find(";</script>")
                if end_script != -1:
                    raw_str = sub[:end_script].strip()
                    return json.loads(raw_str)
            except Exception:
                pass
        return None

    @staticmethod
    def parse_cities(state_data: Optional[Dict[str, Any]] = None) -> List[City]:
        """Returns list of popular cities along with any dynamic regions present in state."""
        cities_dict: Dict[str, City] = {}

        # Add predefined popular cities first
        for pop in CONFIG.POPULAR_CITIES:
            c = City(**pop)
            cities_dict[c.slug] = c

        if state_data and "regions" in state_data:
            # Parse dynamic region if available
            regions_obj = state_data.get("regions", {})
            curr_reg = regions_obj.get("currentRegion", {})
            if isinstance(curr_reg, dict) and "code" in curr_reg:
                code = curr_reg.get("code", "")
                name = curr_reg.get("name", code.capitalize())
                slug = curr_reg.get("slug", name.lower().replace(" ", "-"))
                if slug not in cities_dict:
                    cities_dict[slug] = City(
                        name=name,
                        code=code,
                        slug=slug,
                        state=curr_reg.get("stateName"),
                        is_popular=False,
                    )

        return list(cities_dict.values())

    @staticmethod
    def parse_movies(state_data: Dict[str, Any], city_slug: str, html: Optional[str] = None) -> List[MovieSummary]:
        """Extracts clean movie summaries from getDiscoveryData queries in state or ld+json fallback."""
        movies: List[MovieSummary] = []
        seen_codes = set()

        if state_data:
            explore_api = state_data.get("exploreApi", {})
            queries = explore_api.get("queries", {})

            for q_key, q_val in queries.items():
                if not isinstance(q_val, dict):
                    continue

                q_data = q_val.get("data", {})
                if not isinstance(q_data, dict):
                    continue

                listings = q_data.get("listings", [])
                for listing in listings:
                    if not isinstance(listing, dict):
                        continue

                    cards = listing.get("cards", [])
                    for card in cards:
                        if not isinstance(card, dict):
                            continue

                        # Card identification
                        card_id = card.get("id", "")
                        cta_url = card.get("ctaUrl", "")

                        # Extract event code ET...
                        event_code = card_id
                        if "ET" in cta_url:
                            code_match = re.search(r'(ET\d+)', cta_url)
                            if code_match:
                                event_code = code_match.group(1)

                        if not event_code or event_code in seen_codes:
                            continue

                        # Extract text array components
                        text_items = card.get("text", [])
                        title = ""
                        censor_rating = ""
                        languages = []

                        for t_idx, item in enumerate(text_items):
                            comps = item.get("components", [])
                            t_val = " ".join([c.get("text", "") for c in comps if isinstance(c, dict)]).strip()

                            if t_idx == 0 and t_val:
                                title = t_val
                            elif t_idx == 1 and t_val:
                                censor_rating = t_val
                            elif t_idx == 2 and t_val:
                                languages = [lang.strip() for lang in t_val.split(",") if lang.strip()]

                        if not title:
                            continue

                        # Extract Poster Image
                        image_obj = card.get("image", {})
                        poster_url = image_obj.get("url") if isinstance(image_obj, dict) else None

                        # Extract Rating or Likes if present in image URL or analytics
                        rating_score = None
                        rating_votes = None
                        if poster_url and "ie-" in poster_url:
                            try:
                                import base64
                                ie_match = re.search(r'ie-([A-Za-z0-9+/=]+)', poster_url)
                                if ie_match:
                                    decoded = base64.b64decode(ie_match.group(1)).decode('utf-8', errors='ignore')
                                    if "/" in decoded:
                                        score_part = decoded.split("/")[0]
                                        rating_score = float(score_part)
                                    elif "K" in decoded or "%" in decoded:
                                        rating_votes = decoded
                            except Exception:
                                pass

                        # Build clean detail URL
                        full_detail_url = cta_url if cta_url.startswith("http") else f"{CONFIG.BASE_URL}{cta_url}"
                        movie_slug = cta_url.rstrip("/").split("/")[-2] if "/" in cta_url else event_code.lower()
                        buy_url = f"{CONFIG.BASE_URL}/buytickets/showtimes-{city_slug}/movie-{city_slug}-{event_code}-MT"

                        movies.append(
                            MovieSummary(
                                title=title,
                                code=event_code,
                                slug=movie_slug,
                                rating_score=rating_score,
                                rating_votes=rating_votes,
                                censor_rating=censor_rating,
                                languages=languages,
                                genres=[],
                                poster_url=poster_url,
                                detail_url=full_detail_url,
                                buy_tickets_url=buy_url,
                            )
                        )
                        seen_codes.add(event_code)

        # Fallback: Parse application/ld+json script tags if state yielded no results or few results
        if html and (not movies or len(movies) < 5):
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")
                for script in soup.find_all("script", {"type": "application/ld+json"}):
                    if not script.string and not script.text:
                        continue
                    try:
                        data = json.loads(script.string or script.text)
                        if isinstance(data, dict) and data.get("@type") == "ItemList":
                            for item in data.get("itemListElement", []):
                                if not isinstance(item, dict):
                                    continue
                                url = item.get("url") or item.get("item", {}).get("url") or ""
                                name = item.get("name") or item.get("item", {}).get("name") or ""
                                code_match = re.search(r'(ET\d+)', url)
                                event_code = code_match.group(1) if code_match else ""
                                if event_code and name and event_code not in seen_codes:
                                    movie_slug = url.rstrip("/").split("/")[-2] if "/" in url and len(url.rstrip("/").split("/")) > 1 else event_code.lower()
                                    buy_url = f"{CONFIG.BASE_URL}/buytickets/showtimes-{city_slug}/movie-{city_slug}-{event_code}-MT"
                                    movies.append(
                                        MovieSummary(
                                            title=name,
                                            code=event_code,
                                            slug=movie_slug,
                                            rating_score=None,
                                            rating_votes=None,
                                            censor_rating=None,
                                            languages=[],
                                            genres=[],
                                            poster_url=None,
                                            detail_url=url,
                                            buy_tickets_url=buy_url,
                                        )
                                    )
                                    seen_codes.add(event_code)
                    except Exception:
                        pass
            except Exception:
                pass

        return movies

    @staticmethod
    def parse_events(state_data: Dict[str, Any], city_slug: str, html: Optional[str] = None) -> List[EventSummary]:
        """Extracts clean event summaries from exploreApi state or ld+json fallback."""
        events: List[EventSummary] = []
        seen_codes = set()

        if state_data:
            explore_api = state_data.get("exploreApi", {})
            queries = explore_api.get("queries", {})

            for q_key, q_val in queries.items():
                if not isinstance(q_val, dict):
                    continue

                q_data = q_val.get("data", {})
                if not isinstance(q_data, dict):
                    continue

                listings = q_data.get("listings", [])
                for listing in listings:
                    if not isinstance(listing, dict):
                        continue

                    cards = listing.get("cards", [])
                    for card in cards:
                        if not isinstance(card, dict):
                            continue

                        cta_url = card.get("ctaUrl", "")
                        card_id = card.get("id", "")
                        
                        event_code = card_id
                        code_match = re.search(r'(ET\d+)', cta_url)
                        if code_match:
                            event_code = code_match.group(1)

                        if not event_code or event_code in seen_codes:
                            continue

                        text_items = card.get("text", [])
                        title = ""
                        venue_name = ""
                        date_display = ""
                        price_display = ""

                        for t_idx, item in enumerate(text_items):
                            comps = item.get("components", [])
                            t_val = " ".join([c.get("text", "") for c in comps if isinstance(c, dict)]).strip()
                            if t_idx == 0:
                                title = t_val
                            elif t_idx == 1:
                                venue_name = t_val
                            elif t_idx == 2:
                                date_display = t_val
                            elif t_idx == 3:
                                price_display = t_val

                        if not title:
                            continue

                        image_obj = card.get("image", {})
                        img_url = image_obj.get("url") if isinstance(image_obj, dict) else None
                        full_url = cta_url if cta_url.startswith("http") else f"{CONFIG.BASE_URL}{cta_url}"

                        events.append(
                            EventSummary(
                                title=title,
                                code=event_code,
                                category=listing.get("type", "event"),
                                venue_name=venue_name,
                                date_display=date_display,
                                price_display=price_display,
                                image_url=img_url,
                                detail_url=full_url,
                            )
                        )
                        seen_codes.add(event_code)

        # Fallback: Parse application/ld+json script tags if state yielded no results or few results
        if html and (not events or len(events) < 5):
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")
                for script in soup.find_all("script", {"type": "application/ld+json"}):
                    if not script.string and not script.text:
                        continue
                    try:
                        data = json.loads(script.string or script.text)
                        if isinstance(data, dict) and data.get("@type") == "ItemList":
                            for item_elem in data.get("itemListElement", []):
                                if not isinstance(item_elem, dict):
                                    continue
                                item = item_elem.get("item") if isinstance(item_elem.get("item"), dict) else item_elem
                                url = item.get("url") or item_elem.get("url") or ""
                                name = item.get("name") or item_elem.get("name") or ""
                                code_match = re.search(r'(ET\d+)', url)
                                event_code = code_match.group(1) if code_match else ""
                                if event_code and name and event_code not in seen_codes:
                                    cat = item.get("@type", "Event").replace("Event", "")
                                    loc_obj = item.get("location", {})
                                    venue_name = loc_obj.get("name") if isinstance(loc_obj, dict) else None
                                    date_disp = item.get("startDate", "")
                                    if date_disp and "T" in date_disp:
                                        date_disp = date_disp.split("T")[0]
                                    img_url = item.get("image")
                                    events.append(
                                        EventSummary(
                                            title=name,
                                            code=event_code,
                                            category=cat,
                                            venue_name=venue_name,
                                            date_display=date_disp,
                                            price_display=None,
                                            image_url=img_url,
                                            detail_url=url,
                                        )
                                    )
                                    seen_codes.add(event_code)
                    except Exception:
                        pass
            except Exception:
                pass

        return events


    @staticmethod
    def parse_movie_details(state_data: Dict[str, Any], movie_code: str) -> MovieDetailsResponse:
        """Extracts rich movie metadata, cast, crew, synopsis, and trailers."""
        title = "Unknown Movie"
        synopsis = ""
        duration = None
        release_date = None
        censor_rating = None
        rating_score = None
        rating_votes = None
        languages = []
        genres = []
        poster_url = None
        banner_url = None
        trailers = []
        cast = []
        crew = []

        if not state_data:
            return MovieDetailsResponse(title=title, code=movie_code)

        # Synopsis Movies Api
        syn_api = state_data.get("synopsisMoviesApi", {})
        queries = syn_api.get("queries", {})

        for q_key, q_val in queries.items():
            if not isinstance(q_val, dict):
                continue

            q_data = q_val.get("data", {})
            if not isinstance(q_data, dict):
                continue

            # SEO metadata
            seo = q_data.get("seo", {})
            meta_movies = seo.get("metaMovies", {})
            if meta_movies:
                if not title or title == "Unknown Movie":
                    title = meta_movies.get("title", "").split("- Movie")[0].strip()
                if not synopsis:
                    synopsis = meta_movies.get("description")

            # Banner Widget
            bw = q_data.get("bannerWidget", {})
            if bw and isinstance(bw, dict):
                if not banner_url:
                    banner_url = bw.get("bannerImageUrl")

                multimedia = bw.get("multimedia", {})
                obj_data = multimedia.get("objectData", {}) if isinstance(multimedia, dict) else {}
                if isinstance(obj_data, dict):
                    if not poster_url:
                        poster_url = obj_data.get("imageUrl")
                    meta = obj_data.get("meta", {})
                    if isinstance(meta, dict):
                        lang_objs = meta.get("languages", [])
                        for l in lang_objs:
                            if isinstance(l, dict) and "description" in l:
                                languages.append(l["description"])

                        vids = meta.get("videos", [])
                        for v in vids:
                            if isinstance(v, dict):
                                trailers.append({
                                    "title": v.get("title", "Trailer"),
                                    "url": v.get("videoUrl") or v.get("url"),
                                })

            # Widgets array for Cast / Crew / Synopsis
            widgets = q_data.get("widgets", [])
            for w in widgets:
                if not isinstance(w, dict):
                    continue
                w_id = w.get("id", "").lower()
                w_data = w.get("data")

                if "cast" in w_id or "crew" in w_id:
                    items = w_data if isinstance(w_data, list) else []
                    for item in items:
                        if isinstance(item, dict):
                            c_name = item.get("title") or item.get("name")
                            c_role = item.get("subtitle") or item.get("role")
                            c_img = item.get("imageUrl") or item.get("image", {}).get("url") if isinstance(item.get("image"), dict) else None
                            if c_name:
                                member = CastMember(name=c_name, role=c_role, image_url=c_img)
                                if "cast" in w_id:
                                    cast.append(member)
                                else:
                                    crew.append(member)
                elif "synopsis" in w_id or "about" in w_id:
                    if isinstance(w_data, str):
                        synopsis = w_data

        # Fallback Title from SEO title if needed
        if not title or title == "Unknown Movie":
            seo_data = state_data.get("seo", {}).get("meta", {})
            if "title" in seo_data:
                title = seo_data["title"].split("-")[0].strip()

        return MovieDetailsResponse(
            title=title,
            code=movie_code,
            synopsis=synopsis,
            duration=duration,
            release_date=release_date,
            censor_rating=censor_rating,
            rating_score=rating_score,
            rating_votes=rating_votes,
            languages=list(set(languages)),
            genres=list(set(genres)),
            poster_url=poster_url,
            banner_url=banner_url,
            trailers=trailers,
            cast=cast,
            crew=crew,
            buy_tickets_url=f"{CONFIG.BASE_URL}/buytickets/movie-{movie_code}-MT",
        )

    @staticmethod
    def parse_showtimes(state_data: Dict[str, Any], movie_code: str) -> List[CinemaVenueShowtimes]:
        """Extracts venue showtimes, formats, ticket pricing, and seat availability."""
        venues: List[CinemaVenueShowtimes] = []

        if not state_data:
            return venues

        st_api = state_data.get("showtimesFunctionalApi", {})
        queries = st_api.get("queries", {})

        for q_key, q_val in queries.items():
            if not isinstance(q_val, dict) or "fetchPrimaryDynamic" not in q_key:
                continue

            q_data = q_val.get("data", {}).get("data", {})
            if not isinstance(q_data, dict):
                continue

            showtime_widgets = q_data.get("showtimeWidgets", [])
            for widget in showtime_widgets:
                if not isinstance(widget, dict):
                    continue

                widget_data = widget.get("data", [])
                for group in widget_data:
                    if not isinstance(group, dict):
                        continue

                    venue_items = group.get("data", [])
                    for v_item in venue_items:
                        if not isinstance(v_item, dict):
                            continue

                        add_data = v_item.get("additionalData", {})
                        venue_code = add_data.get("venueCode", "")
                        venue_name = add_data.get("venueName", "")
                        is_m_ticket = add_data.get("isMTicketAvailable", True)

                        if not venue_name and "header" in v_item:
                            # Header component fallback
                            h_comps = v_item.get("header", {}).get("data", {}).get("components", [])
                            for hc in h_comps:
                                if hc.get("type") == "text":
                                    for sub_c in hc.get("data", {}).get("data", []):
                                        for comp in sub_c.get("components", []):
                                            if comp.get("text"):
                                                venue_name = comp.get("text")
                                                break

                        if not venue_name:
                            continue

                        # Extract Showtimes Sections
                        showtimes_list: List[ShowtimeItem] = []
                        sec_list = v_item.get("showtimesSections", [])

                        for sec in sec_list:
                            if not isinstance(sec, dict):
                                continue

                            sec_title = sec.get("title")
                            st_slots = sec.get("showtimes", [])

                            for slot in st_slots:
                                if not isinstance(slot, dict):
                                    continue

                                show_time = (
                                    slot.get("showTime")
                                    or slot.get("title")
                                    or slot.get("additionalData", {}).get("showTime")
                                )
                                category = slot.get("showTimeCategory")
                                availability_raw = (
                                    slot.get("availability")
                                    or slot.get("additionalData", {}).get("availStatus")
                                    or "AVAILABLE"
                                )
                                format_name = (
                                    slot.get("screenAttr")
                                    or slot.get("additionalData", {}).get("attributes")
                                    or sec_title
                                    or "2D"
                                )

                                # Price extraction
                                price_list = slot.get("priceList", [])
                                prices: List[float] = []

                                if price_list:
                                    prices.extend(
                                        [float(p.get("price", 0)) for p in price_list if isinstance(p, dict) and "price" in p]
                                    )

                                if not prices:
                                    # Fallback: Extract seat category prices from customGestureCTA / bottomSheetData
                                    import re
                                    widgets = (
                                        slot.get("customGestureCTA", {})
                                        .get("additionalData", {})
                                        .get("bottomSheetData", {})
                                        .get("widgets", [])
                                    )
                                    for w in widgets:
                                        if isinstance(w, dict) and w.get("layoutId") == "seat-category-type-available":
                                            cost_str = w.get("variableData", {}).get("seatCost", "")
                                            cost_match = re.search(r'[\d,]+(?:\.\d+)?', cost_str.replace(',', ''))
                                            if cost_match:
                                                try:
                                                    prices.append(float(cost_match.group(0)))
                                                except ValueError:
                                                    pass

                                price_min = min(prices) if prices else None
                                price_max = max(prices) if prices else None

                                if show_time:
                                    showtimes_list.append(
                                        ShowtimeItem(
                                            show_time=show_time,
                                            show_time_category=category,
                                            format=format_name,
                                            price_min=price_min,
                                            price_max=price_max,
                                            availability=availability_raw,
                                            is_m_ticket_supported=is_m_ticket,
                                        )
                                    )

                        venues.append(
                            CinemaVenueShowtimes(
                                venue_code=venue_code or "VENUE",
                                venue_name=venue_name,
                                address_info=None,
                                distance_km=None,
                                is_m_ticket=is_m_ticket,
                                showtimes=showtimes_list,
                            )
                        )

        return venues

    @staticmethod
    def parse_venue_details(state_data: Dict[str, Any], venue_code: str) -> Optional[VenueDetailsResponse]:
        """Extracts venue metadata including address, latitude, longitude, and facilities."""
        if not state_data:
            return None

        v_api = state_data.get("venueShowtimesFunctionalApi", {})
        queries = v_api.get("queries", {})

        for q_key, q_val in queries.items():
            if not isinstance(q_val, dict) or "getVenueShowcaseDetails" not in q_key:
                continue

            q_data = q_val.get("data", {}).get("data", {})
            if not isinstance(q_data, dict) or not q_data.get("venueName"):
                continue

            v_code = q_data.get("venueCode") or venue_code
            v_name = q_data.get("venueName")
            v_addr = q_data.get("venueAddress")

            lat = None
            lon = None
            if q_data.get("latitude"):
                try:
                    lat = float(q_data.get("latitude"))
                except (ValueError, TypeError):
                    pass
            if q_data.get("longitude"):
                try:
                    lon = float(q_data.get("longitude"))
                except (ValueError, TypeError):
                    pass

            facilities = []
            fac_obj = q_data.get("venueFacilities", {})
            if isinstance(fac_obj, dict):
                facilities = [
                    f.get("text") for f in fac_obj.get("facilities", [])
                    if isinstance(f, dict) and f.get("text")
                ]

            return VenueDetailsResponse(
                venue_code=v_code,
                venue_name=v_name,
                address=v_addr,
                latitude=lat,
                longitude=lon,
                facilities=facilities,
            )

        return None


