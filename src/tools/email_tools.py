from datetime import datetime

from jinja2 import Environment, FileSystemLoader


def create_email_from_template(top_posts, group_name, group_link, platform_alias, external_id):
    env = Environment(loader=FileSystemLoader('src/templates/'))
    template = env.get_template('top_posts_email_template.j2')
    content = template.render(
        data=top_posts,
        updated_at=datetime.now().strftime('%Y-%m-%d'),
        group_name=group_name,
        group_link=group_link,
        platform_alias=platform_alias,
        external_id=external_id,
    )

    return content

