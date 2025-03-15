
import os
import io
from typing import Annotated
import uuid
from xml.dom.minidom import Document, Element

from fastapi import Depends

from src.services.cos_service import CosService, CosServiceDep
from src.core.constants import ContentFileType
from src.models.episode import Episode
from src.models.podcast import Podcast
from src.config.settings import settings


class RssService:

    def __init__(self, cos_service: CosService):

        self.cos_service = cos_service
        self.podcast = None

    def update_podcast_rss(self, podcast: Podcast):

        self.podcast = podcast

        self._delete_existing_rss_xml()
        xml_doc = self._generate_rss()

        if not xml_doc:
            return

        xml_str = xml_doc.toxml().encode('utf-8')
        xml_binary_io = io.BytesIO(xml_str)
        xml_filename = f"users/{self.podcast.author_id}/podcasts/{self.podcast.id}/rss"
        self.cos_service.save_file(xml_binary_io, xml_filename)
        self.podcast.feed_path = xml_filename

    def _generate_rss(self) -> Document:

        if not self._check_podcast_integrity():
            return

        itunes_namespace_url = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        content_namespace_url = "http://purl.org/rss/1.0/modules/content/"

        xml_doc = Document()

        rss_element = xml_doc.createElement("rss")
        xml_doc.appendChild(rss_element)

        rss_element.setAttribute("version", "2.0")
        rss_element.setAttribute("xmlns:itunes", itunes_namespace_url)
        rss_element.setAttribute("xmlns:content", content_namespace_url)

        channel_element = xml_doc.createElement("channel")
        rss_element.appendChild(channel_element)

        self._populate_channel_element(xml_doc, channel_element)

        return xml_doc

    def _write_xml_to_file(self, xml_doc: Document) -> str:

        unique_filename = uuid.uuid4().hex + ".xml"
        target_dir = os.path.join(
            settings.CONTENTS_DIR, ContentFileType.RSS_XML.value)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        filename = os.path.join(target_dir, unique_filename)

        with open(filename, 'w', encoding="UTF-8") as file:
            xml_doc.writexml(file, encoding="UTF-8")

        return filename

    def _populate_channel_element(self, xml_doc: Document, channel_element: Element):

        title = xml_doc.createElement("title")
        channel_element.appendChild(title)
        title.appendChild(xml_doc.createTextNode(self.podcast.title))

        description = xml_doc.createElement("description")
        channel_element.appendChild(description)
        description.appendChild(
            xml_doc.createTextNode(self.podcast.description))

        itunes_image = xml_doc.createElement("itunes:image")
        channel_element.appendChild(itunes_image)
        itunes_image.setAttribute("href", self._get_content_url(
            self.podcast.id, ContentFileType.PODCAST_COVER))

        language = xml_doc.createElement("language")
        channel_element.appendChild(language)
        language.appendChild(xml_doc.createTextNode(self.podcast.language))

        itunes_category = xml_doc.createElement("itunes:category")
        channel_element.appendChild(itunes_category)
        itunes_category.setAttribute("text", self.podcast.itunes_category)

        if self.podcast.itunes_subcategory:
            itunes_subcategory = xml_doc.createElement("itunes:category")
            itunes_category.appendChild(itunes_subcategory)
            itunes_subcategory.setAttribute(
                "text", self.podcast.itunes_subcategory)

        itunes_explicit = xml_doc.createElement("itunes:explicit")
        channel_element.appendChild(itunes_explicit)
        itunes_explicit.appendChild(
            xml_doc.createTextNode(str(self.podcast.itunes_explicit)))

        if self.podcast.author:
            author = xml_doc.createElement("author")
            channel_element.appendChild(author)
            author.appendChild(xml_doc.createTextNode(
                self.podcast.author.nickname))

        if self.podcast.link:
            link = xml_doc.createElement("link")
            channel_element.appendChild(link)
            link.appendChild(xml_doc.createTextNode(self.podcast.link))

        if self.podcast.copyright:
            copyright = xml_doc.createElement("copyright")
            channel_element.appendChild(copyright)
            copyright.appendChild(
                xml_doc.createTextNode(self.podcast.copyright))

        if self.podcast.generator:
            generator = xml_doc.createElement("generator")
            channel_element.appendChild(generator)
            generator.appendChild(
                xml_doc.createTextNode(self.podcast.generator))

        self._add_items(xml_doc, channel_element)

    def _add_items(self, xml_doc: Document, channel_element: Element):

        for episode in self.podcast.episodes:

            if not self._check_episode_integrity(episode):
                continue

            item = xml_doc.createElement("item")
            channel_element.appendChild(item)

            self._populate_item_element(episode, xml_doc, item)

    def _populate_item_element(self, episode: Episode, xml_doc: Document, item_element: Element):

        title = xml_doc.createElement("title")
        item_element.appendChild(title)
        title.appendChild(xml_doc.createTextNode(episode.title))

        enclosure = xml_doc.createElement("enclosure")
        item_element.appendChild(enclosure)
        enclosure.setAttribute("url", self._get_content_url(
            episode.id, ContentFileType.AUDIO))
        enclosure.setAttribute("length", str(episode.enclosure_length))
        enclosure.setAttribute("type", episode.enclosure_type)

        guid = xml_doc.createElement("guid")
        item_element.appendChild(guid)
        guid.appendChild(xml_doc.createTextNode(episode.guid))

        if episode.pub_date:
            pub_date = xml_doc.createElement("pubDate")
            item_element.appendChild(pub_date)
            pub_date.appendChild(xml_doc.createTextNode(episode.pub_date))

        if episode.description:
            description = xml_doc.createElement("description")
            item_element.appendChild(description)
            description.appendChild(
                xml_doc.createTextNode(episode.description))

        if episode.itunes_duration:
            itunes_duration = xml_doc.createElement("itunes_duration")
            item_element.appendChild(itunes_duration)
            itunes_duration.appendChild(
                xml_doc.createTextNode(str(episode.itunes_duration)))

        if episode.link:
            title = xml_doc.createElement("title")
            item_element.appendChild(title)
            title.appendChild(xml_doc.createTextNode(episode.title))

        if episode.itunes_image_path:
            itunes_image = xml_doc.createElement("itunes:image")
            item_element.appendChild(itunes_image)
            itunes_image.setAttribute("href", self._get_content_url(
                episode.id, ContentFileType.EPISODE_COVER))

        if episode.itunes_explicit:
            itunes_image = xml_doc.createElement("itunes:image")
            item_element.appendChild(itunes_image)
            itunes_image.appendChild(xml_doc.createTextNode(
                "true" if episode.itunes_explicit else "false"
            ))

    def _check_podcast_integrity(self) -> bool:

        if not (
            self.podcast.episodes
            and self.podcast.title
            and self.podcast.description
            and self.podcast.language
            and self.podcast.itunes_category
            and self.podcast.itunes_subcategory
        ):
            return False

        return True

    def _check_episode_integrity(self, episode: Episode) -> bool:

        return episode.title and \
            episode.enclosure_path and \
            episode.enclosure_length and \
            episode.enclosure_type

    def _get_content_url(self, id: int, filetype: ContentFileType) -> str:

        if filetype == ContentFileType.PODCAST_COVER:
            return settings.BASE_URL + "/".join(["podcasts", str(id), "cover"])

        if filetype == ContentFileType.EPISODE_COVER:
            return settings.BASE_URL + "/".join(["episodes", str(id), "cover"])

        if filetype == ContentFileType.AUDIO:
            return settings.BASE_URL + "/".join(["episodes", str(id), "audio"])

    def _delete_existing_rss_xml(self):

        if self.podcast.feed_path:
            self.cos_service.delete_file(self.podcast.feed_path)


def get_rss_service(cos_service: CosServiceDep):
    return RssService(cos_service)


RssServiceDep = Annotated[RssService, Depends(get_rss_service)]
