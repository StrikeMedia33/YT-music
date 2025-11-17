"""
Trello API Manager for Project Management
Handles all Trello API operations for the project manager agent
"""

import os
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

class TrelloManager:
    """Core Trello API integration for project management"""
    
    def __init__(self):
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.board_id = os.getenv('TRELLO_BOARD_ID')

        if not all([self.api_key, self.token, self.board_id]):
            raise ValueError("Missing Trello credentials. Check your .env file.")

        self.base_url = "https://api.trello.com/1"
        self.auth_params = {
            'key': self.api_key,
            'token': self.token
        }

        # Connection pooling for performance (reuses TCP connections)
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})

        # Cache for list and label IDs
        self._lists_cache = None
        self._labels_cache = None
        self._custom_fields_cache = None
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Any:
        """Make authenticated request to Trello API using connection pooling"""
        url = f"{self.base_url}{endpoint}"
        request_params = {**self.auth_params, **(params or {})}
        timeout = 30  # 30 second timeout

        try:
            # Use session for connection pooling (HTTP keep-alive)
            response = self.session.request(
                method,
                url,
                params=request_params,
                json=data,
                timeout=timeout
            )

            response.raise_for_status()
            return response.json() if response.text else None

        except requests.exceptions.RequestException as e:
            print(f"❌ Trello API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    # ============================================================================
    # LISTS MANAGEMENT
    # ============================================================================
    
    def get_lists(self, force_refresh: bool = False) -> Dict[str, str]:
        """Get all lists on the board (cached)"""
        if self._lists_cache is None or force_refresh:
            lists = self._make_request('GET', f'/boards/{self.board_id}/lists')
            self._lists_cache = {lst['name']: lst['id'] for lst in lists}
        return self._lists_cache
    
    def get_list_id(self, list_name: str) -> Optional[str]:
        """Get list ID by name"""
        lists = self.get_lists()
        return lists.get(list_name)
    
    # ============================================================================
    # LABELS MANAGEMENT
    # ============================================================================
    
    def get_labels(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """Get all labels on the board (cached)"""
        if self._labels_cache is None or force_refresh:
            labels = self._make_request('GET', f'/boards/{self.board_id}/labels')
            self._labels_cache = {
                label['name']: {
                    'id': label['id'],
                    'color': label['color']
                }
                for label in labels if label['name']
            }
        return self._labels_cache
    
    def get_label_ids(self, label_names: List[str]) -> List[str]:
        """Convert label names to IDs"""
        labels = self.get_labels()
        return [labels[name]['id'] for name in label_names if name in labels]
    
    # ============================================================================
    # CUSTOM FIELDS MANAGEMENT
    # ============================================================================
    
    def get_custom_fields(self, force_refresh: bool = False) -> Dict[str, str]:
        """Get all custom fields on the board (cached)"""
        if self._custom_fields_cache is None or force_refresh:
            fields = self._make_request('GET', f'/boards/{self.board_id}/customFields')
            self._custom_fields_cache = {field['name']: field['id'] for field in fields}
        return self._custom_fields_cache
    
    def get_custom_field_id(self, field_name: str) -> Optional[str]:
        """Get custom field ID by name"""
        fields = self.get_custom_fields()
        return fields.get(field_name)
    
    def set_custom_field_value(self, card_id: str, field_name: str, value: str):
        """Set custom field value on a card"""
        field_id = self.get_custom_field_id(field_name)
        if not field_id:
            print(f"⚠️  Custom field '{field_name}' not found")
            return
        
        endpoint = f'/card/{card_id}/customField/{field_id}/item'
        data = {'value': {'text': value}}
        self._make_request('PUT', endpoint, data=data)
    
    # ============================================================================
    # CARDS - READ OPERATIONS
    # ============================================================================
    
    def get_cards_in_list(self, list_name: str) -> List[Dict]:
        """Get all cards in a specific list"""
        list_id = self.get_list_id(list_name)
        if not list_id:
            print(f"⚠️  List '{list_name}' not found")
            return []
        
        cards = self._make_request('GET', f'/lists/{list_id}/cards', {
            'customFieldItems': 'true',
            'fields': 'name,desc,due,labels,idList,id,dateLastActivity'
        })
        
        return cards
    
    def get_all_cards(self) -> Dict[str, List[Dict]]:
        """Get all cards organized by list name"""
        lists = self.get_lists()
        board_cards = {}
        
        for list_name, list_id in lists.items():
            cards = self._make_request('GET', f'/lists/{list_id}/cards', {
                'customFieldItems': 'true',
                'fields': 'name,desc,due,labels,idList,id,dateLastActivity'
            })
            board_cards[list_name] = cards
        
        return board_cards
    
    def search_cards(self, query: str) -> List[Dict]:
        """Search for cards across the board"""
        params = {
            'query': query,
            'modelTypes': 'cards',
            'card_fields': 'name,desc,due,labels,idList',
            'cards_limit': 50
        }
        
        results = self._make_request('GET', '/search', params)
        return results.get('cards', [])
    
    # ============================================================================
    # CARDS - CREATE & UPDATE OPERATIONS
    # ============================================================================
    
    def create_card(
        self,
        list_name: str,
        title: str,
        description: str = "",
        urgency: str = None,  # 🔴, 🟠, or 🟢
        labels: List[str] = None,
        due_date: str = None,  # ISO format or DD-MM-YYYY
        documentation_link: str = None,
        position: str = "top"
    ) -> Dict:
        """
        Create a new card with formatted title and metadata
        
        Args:
            list_name: Name of the list to create card in
            title: Card title (urgency emoji will be prepended)
            description: Card description (markdown supported)
            urgency: Urgency level - 🔴 (Urgent), 🟠 (Intermediate), 🟢 (Not Urgent)
            labels: List of label names to apply
            due_date: Due date string
            documentation_link: URL to implementation doc (added to description)
            position: Card position in list ('top' or 'bottom')
        """
        list_id = self.get_list_id(list_name)
        if not list_id:
            raise ValueError(f"List '{list_name}' not found")
        
        # Format title with urgency emoji
        formatted_title = f"{urgency} {title}" if urgency else title
        
        # Add documentation link to description if provided
        formatted_description = description
        if documentation_link:
            if formatted_description:
                formatted_description += f"\n\n---\n**Documentation:** {documentation_link}"
            else:
                formatted_description = f"**Documentation:** {documentation_link}"
        
        # Convert label names to IDs
        label_ids = []
        if labels:
            label_ids = self.get_label_ids(labels)
            
            # Add urgency label if specified
            urgency_label_map = {
                '🔴': 'Urgent',
                '🟠': 'Intermediate', 
                '🟢': 'Not Urgent'
            }
            if urgency and urgency in urgency_label_map:
                urgency_label_name = urgency_label_map[urgency]
                urgency_label_id = self.get_label_ids([urgency_label_name])
                if urgency_label_id:
                    label_ids.extend(urgency_label_id)
        
        # Parse due date if provided
        parsed_due = None
        if due_date:
            parsed_due = self._parse_date(due_date)
        
        # Create card
        data = {
            'idList': list_id,
            'name': formatted_title,
            'desc': formatted_description,
            'pos': position,
            'idLabels': label_ids
        }
        
        if parsed_due:
            data['due'] = parsed_due
        
        card = self._make_request('POST', '/cards', data=data)
        
        print(f"✅ Created card: {formatted_title}")
        return card
    
    def update_card(
        self,
        card_id: str,
        title: str = None,
        description: str = None,
        urgency: str = None,
        labels: List[str] = None,
        due_date: str = None,
        documentation_link: str = None
    ) -> Dict:
        """Update an existing card"""
        data = {}

        if title:
            # OPTIMIZATION: Only fetch card if we need to check/replace urgency emoji
            if urgency:
                # Need to check existing urgency emoji
                current_card = self._make_request('GET', f'/cards/{card_id}')
                current_title = current_card['name']

                # Check if title already has urgency emoji
                has_urgency = any(emoji in current_title for emoji in ['🔴', '🟠', '🟢'])

                if not has_urgency:
                    data['name'] = f"{urgency} {title}"
                else:
                    # Replace existing urgency
                    for emoji in ['🔴', '🟠', '🟢']:
                        if emoji in current_title:
                            data['name'] = current_title.replace(emoji, urgency, 1)
                            break
            else:
                # No urgency specified, just update title
                data['name'] = title

        if description is not None:
            formatted_description = description
            # Add documentation link to description if provided
            if documentation_link:
                if formatted_description:
                    formatted_description += f"\n\n---\n**Documentation:** {documentation_link}"
                else:
                    formatted_description = f"**Documentation:** {documentation_link}"
            data['desc'] = formatted_description

        if labels is not None:
            label_ids = self.get_label_ids(labels)
            data['idLabels'] = label_ids

        if due_date:
            data['due'] = self._parse_date(due_date)

        if data:
            card = self._make_request('PUT', f'/cards/{card_id}', data=data)
        else:
            card = self._make_request('GET', f'/cards/{card_id}')

        print(f"🔄 Updated card: {card['name']}")
        return card
    
    def move_card(
        self,
        card_id: str,
        destination_list: str,
        position: str = "top",
        mark_complete: bool = False
    ) -> Dict:
        """
        Move card to a different list

        Args:
            card_id: ID of card to move
            destination_list: Name of destination list
            position: Position in new list ('top' or 'bottom')
            mark_complete: If True, add ✅ emoji and remove urgency emoji
        """
        list_id = self.get_list_id(destination_list)
        if not list_id:
            raise ValueError(f"List '{destination_list}' not found")

        data = {
            'idList': list_id,
            'pos': position
        }

        # OPTIMIZATION: Only fetch card if we need to modify title
        if mark_complete:
            card = self._make_request('GET', f'/cards/{card_id}')
            current_title = card['name']

            # Remove urgency emoji and add ✅ at the end
            new_title = current_title
            for emoji in ['🔴', '🟠', '🟢']:
                new_title = new_title.replace(emoji, '').strip()

            if '✅' not in new_title:
                new_title = f"{new_title} ✅"

            data['name'] = new_title

        updated_card = self._make_request('PUT', f'/cards/{card_id}', data=data)

        print(f"📦 Moved card to {destination_list}: {updated_card['name']}")
        return updated_card
    
    def archive_card(self, card_id: str) -> Dict:
        """Archive (close) a card"""
        card = self._make_request('PUT', f'/cards/{card_id}', data={'closed': True})
        print(f"📁 Archived card: {card['name']}")
        return card

    # ============================================================================
    # ATTACHMENTS - IMAGE HANDLING
    # ============================================================================

    def get_attachments(self, card_id: str) -> List[Dict]:
        """
        Get all attachments from a card

        Args:
            card_id: ID of the card to get attachments from

        Returns:
            List of attachment objects with id, name, url, mimeType, etc.
        """
        attachments = self._make_request('GET', f'/cards/{card_id}/attachments')
        return attachments

    def attach_url(self, card_id: str, url: str, name: str = None) -> Dict:
        """
        Attach an image or file from a URL to a card

        Args:
            card_id: ID of the card to attach to
            url: Public URL of the image/file
            name: Optional name for the attachment

        Returns:
            Attachment object
        """
        params = {'url': url}
        if name:
            params['name'] = name

        attachment = self._make_request('POST', f'/cards/{card_id}/attachments', params=params)
        print(f"🖼️  Attached {name or 'image'} to card")
        return attachment

    def copy_attachments(self, source_card_id: str, destination_card_id: str) -> List[Dict]:
        """
        Copy all attachments from one card to another

        This method downloads actual uploaded files and re-uploads them to the destination card.
        URL-only attachments are copied as URL references.

        Args:
            source_card_id: ID of the card to copy attachments from
            destination_card_id: ID of the card to copy attachments to

        Returns:
            List of newly created attachment objects
        """
        source_attachments = self.get_attachments(source_card_id)

        if not source_attachments:
            print("ℹ️  No attachments to copy")
            return []

        new_attachments = []
        for attachment in source_attachments:
            # Skip deleted or invalid attachments
            if not attachment.get('url'):
                continue

            # Check if this is an actual uploaded file (has file data)
            is_uploaded_file = attachment.get('isUpload') and attachment.get('bytes')

            if is_uploaded_file:
                # Download and re-upload the actual file
                print(f"📥 Downloading {attachment.get('name')}...")
                try:
                    # Download the file content with OAuth authentication
                    headers = {
                        'Authorization': f'OAuth oauth_consumer_key="{self.api_key}", oauth_token="{self.token}"'
                    }
                    response = requests.get(attachment['url'], headers=headers)
                    response.raise_for_status()

                    # Prepare file upload
                    files = {
                        'file': (
                            attachment.get('name', 'attachment'),
                            response.content,
                            attachment.get('mimeType', 'application/octet-stream')
                        )
                    }

                    # Upload to destination card
                    upload_url = f"{self.base_url}/cards/{destination_card_id}/attachments"
                    upload_response = self.session.post(
                        upload_url,
                        params=self.auth_params,
                        files=files,
                        timeout=60  # Longer timeout for file uploads
                    )
                    upload_response.raise_for_status()

                    new_attachment = upload_response.json()
                    new_attachments.append(new_attachment)
                    print(f"📤 Uploaded {attachment.get('name')} to new card")

                except requests.exceptions.RequestException as e:
                    print(f"⚠️  Failed to copy {attachment.get('name')}: {e}")
                    continue

            else:
                # Just a URL reference - copy as-is
                new_attachment = self.attach_url(
                    card_id=destination_card_id,
                    url=attachment['url'],
                    name=attachment.get('name')
                )
                new_attachments.append(new_attachment)
                print(f"🔗 Linked URL attachment: {attachment.get('name')}")

        print(f"🖼️  Copied {len(new_attachments)} attachment(s) to new card")
        return new_attachments

    def create_card_from_voice_note(
        self,
        voice_note_card: Dict,
        list_name: str,
        title: str,
        description: str = "",
        urgency: str = None,
        labels: List[str] = None,
        due_date: str = None,
        documentation_link: str = None,
        position: str = "top"
    ) -> Dict:
        """
        Create a structured task card from a voice note, automatically preserving attachments

        This method ensures images are ALWAYS copied from voice notes to new task cards,
        preventing the common mistake of forgetting to transfer attachments manually.

        Args:
            voice_note_card: The source voice note card object (must have 'id' key)
            list_name: Name of the list to create the new card in
            title: Card title (urgency emoji will be prepended)
            description: Card description (markdown supported)
            urgency: Urgency level - 🔴 (Urgent), 🟠 (Intermediate), 🟢 (Not Urgent)
            labels: List of label names to apply
            due_date: Due date string
            documentation_link: URL to implementation doc (added to description)
            position: Card position in list ('top' or 'bottom')

        Returns:
            Dict containing:
                - 'card': The newly created card object
                - 'attachments_copied': Number of attachments transferred
                - 'comment_added': Boolean indicating if audit comment was added
        """
        # Step 1: Create the new card using existing create_card method
        new_card = self.create_card(
            list_name=list_name,
            title=title,
            description=description,
            urgency=urgency,
            labels=labels,
            due_date=due_date,
            documentation_link=documentation_link,
            position=position
        )

        # Step 2: ALWAYS copy attachments from voice note (can't be forgotten)
        attachments = self.copy_attachments(
            source_card_id=voice_note_card['id'],
            destination_card_id=new_card['id']
        )

        # Step 3: Add audit trail comment documenting the transfer
        comment_text = f"**Created from voice note:** {voice_note_card.get('name', 'Untitled')}"
        if attachments:
            comment_text += f"\n**Images preserved:** {len(attachments)} attachment(s) transferred"
        else:
            comment_text += "\n**Note:** Original voice note had no attachments"

        self.add_comment(card_id=new_card['id'], comment=comment_text)

        print(f"✅ Created card from voice note with {len(attachments)} attachment(s)")

        return {
            'card': new_card,
            'attachments_copied': len(attachments),
            'comment_added': True
        }

    def add_comment(self, card_id: str, comment: str) -> Dict:
        """
        Add a comment to a card for audit trail tracking

        Args:
            card_id: ID of the card to comment on
            comment: Comment text (markdown supported)

        Returns:
            Dict containing the comment action data
        """
        endpoint = f'/cards/{card_id}/actions/comments'
        params = {'text': comment}

        comment_action = self._make_request('POST', endpoint, params=params)
        print(f"💬 Added comment to card")
        return comment_action

    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats to ISO format"""
        # Already ISO format
        if 'T' in date_str:
            return date_str
        
        # DD-MM-YYYY format
        try:
            dt = datetime.strptime(date_str, '%d-%m-%Y')
            return dt.isoformat()
        except ValueError:
            pass
        
        # Try other common formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        raise ValueError(f"Could not parse date: {date_str}")
    
    def format_card_summary(self, card: Dict) -> str:
        """Format card data into readable summary"""
        name = card['name']
        desc = card.get('desc', '')[:100] + '...' if card.get('desc') else 'No description'
        labels_str = ', '.join([label['name'] for label in card.get('labels', [])])
        due = card.get('due', 'No due date')
        
        return f"""
📋 {name}
   Labels: {labels_str or 'None'}
   Due: {due}
   Description: {desc}
"""
    
    def get_board_summary(self) -> str:
        """Get formatted summary of entire board"""
        all_cards = self.get_all_cards()
        
        summary = ["=" * 60, "📊 TRELLO BOARD SUMMARY", "=" * 60, ""]
        
        for list_name, cards in all_cards.items():
            summary.append(f"\n## {list_name} ({len(cards)} cards)")
            summary.append("-" * 60)
            
            if not cards:
                summary.append("  (empty)")
            else:
                for card in cards:
                    urgency = ""
                    for emoji in ['🔴', '🟠', '🟢']:
                        if emoji in card['name']:
                            urgency = emoji
                            break
                    
                    labels = [label['name'] for label in card.get('labels', [])]
                    label_str = f" [{', '.join(labels)}]" if labels else ""
                    
                    summary.append(f"  {urgency} {card['name']}{label_str}")
            
            summary.append("")
        
        return "\n".join(summary)

    def __del__(self):
        """Clean up session on destruction"""
        if hasattr(self, 'session'):
            self.session.close()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_add_task(
    title: str,
    list_name: str = "Backlog",
    urgency: str = "🟢",
    description: str = "",
    labels: List[str] = None
):
    """Quick function to add a task"""
    manager = TrelloManager()
    return manager.create_card(
        list_name=list_name,
        title=title,
        description=description,
        urgency=urgency,
        labels=labels
    )


def move_to_review(card_id: str):
    """Quick function to move card to review"""
    manager = TrelloManager()
    return manager.move_card(card_id, "To Review")


def mark_complete(card_id: str):
    """Quick function to mark card complete"""
    manager = TrelloManager()
    return manager.move_card(card_id, "Completed", mark_complete=True)


def get_board_status():
    """Quick function to see board status"""
    manager = TrelloManager()
    print(manager.get_board_summary())


if __name__ == "__main__":
    # Test connection
    manager = TrelloManager()
    print("✅ Trello connection successful!")
    print(f"Board ID: {manager.board_id}")
    print(f"\nLists found: {', '.join(manager.get_lists().keys())}")
    print(f"Labels found: {', '.join(manager.get_labels().keys())}")