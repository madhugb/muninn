import webapp2
import jinja2
import os
import json

from muninn.agents import Agent, URLFetchAgent, PrintEventsAgent,\
     MailAgent
from muninn.agents.hipchat import HipchatAgent
from muninn.models import AgentStore, cls_from_name


templates = jinja2.Environment(loader=jinja2.FileSystemLoader(
    os.path.join(os.path.dirname(__file__), 'templates')
))

class BaseHandler(webapp2.RequestHandler):
    pass


class TestAgents(BaseHandler):
    def get(self):
        urlfetchagent = URLFetchAgent.new(
            'IP Fetcher',
            config={
                'url': 'http://ip.jsontest.com',
                'extract': {
                    'ip': '$.ip',
                    'titi': '$.ip'
                }
            })

        printagent = PrintEventsAgent.new(
            'Print Agent',
            source_agents=[urlfetchagent])

        #HipchatAgent.new(
        #    'Hipchat Agent',
        #    config={
        #        'token': 'XYZ',
        #        'template_message': 'The IP is {{ data[0].ip }}',
        #        'room_id': '122569'
        #    },
        #    source_agents=[urlfetchagent])


class RunAllAgents(BaseHandler):
    def get(self):
        agents = AgentStore.all()
        self.response.content_type = 'text/plain'
        for agent in agents:
            self.response.out.write('Running ' + agent.name + '\n')
            agent.run()


class ListAllAgents(BaseHandler):
    def get(self):
        agents = AgentStore.all()
        template = templates.get_template('list_all_agents.html')
        return self.response.out.write(template.render({'agents': agents}))


class AddAgent(BaseHandler):
    def get(self):
        # TODO: don't hard code this dict
        registered_agents = {
            'URL Fetch Agent': URLFetchAgent,
            'Print Events Agent': PrintEventsAgent,
            'Mail Agent': MailAgent
        }
        agents = AgentStore.all()
        template = templates.get_template('add_agent.html')
        return self.response.out.write(template.render({
            'registered_agents': registered_agents,
            'agents': agents
        }))

    def post(self):
        agent_type = self.request.get('agent_type')
        name = self.request.get('name')
        sources = self.request.get('sources')
        config = self.request.get('config')
        config = json.loads(config)
        sources = sources.split(',')
        sources = [s.strip() for s in sources]
        source_agents = AgentStore.query(
            AgentStore.name.IN(sources),
            AgentStore.is_active == True
        ).fetch()
        agent_cls = cls_from_name(agent_type)
        agent = agent_cls.new(name,
                              source_agents=source_agents,
                              config=config)
        template = templates.get_template('add_agent.html')
        return self.response.out.write(template.render({
            'agent': agent
        }))



app = webapp2.WSGIApplication([
    ('/agents/test/?', TestAgents),
    ('/agents/all/run/?', RunAllAgents),
    ('/agents/all/?', ListAllAgents),
    ('/agents/add/?', AddAgent),
], debug=True)