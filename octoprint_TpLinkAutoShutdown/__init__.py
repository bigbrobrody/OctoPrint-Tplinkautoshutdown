# coding=utf-8
from __future__ import absolute_import
from .TpLinkHandler import TpLinkHandler as wallPlug
import octoprint.plugin
import flask


class TpLinkAutoShutdown(octoprint.plugin.StartupPlugin, octoprint.plugin.SettingsPlugin,
						 octoprint.plugin.EventHandlerPlugin, octoprint.plugin.TemplatePlugin,
						 octoprint.plugin.AssetPlugin, octoprint.plugin.SimpleApiPlugin):

	def on_after_startup(self):
		self._logger.info("Plugin TpLinkHandler has started")
		try:
			self.conn = _conn = wallPlug(self._settings.get(["url"]))
			self.conn.update()
			self._logger.info(self.conn.get_plug_information())
		except:
			self._logger.info("+++++++++++ Can't connect to plug +++++++++++++")

	def on_event(self, event, payload):
		if event == "PrintDone":
			self._logger.info(f"The print has completed. Auto-shutdown is set to {self._settings.get(['auto'])}")
			if self._settings.get(["auto"]) and self._settings.get(["movieDone"]) == False:
				self._logger.info("Printer is being shutdown")
				self.conn.shutdown()
		elif event == "PrintStarted":
			self._logger.info(str(self._settings.get(["auto"])))
			self._logger.info("Print has been started")
			self.conn = wallPlug(self._settings.get(["url"]))
			self.conn.update()
		elif event == "MovieDone":
			if self._settings.get(["movieDone"]) and self._settings.get(["auto"]):
				self.conn.shutdown()
		elif event == "PrintPaused":
			self._logger.info("Print paused")

	def get_api_commands(self):
		return dict(
			turnOn=[],
			turnOff=[],
			update=["url"]
		)

	def on_api_command(self, command, data):
		if command == "turnOn":
			self._logger.info("Turning the printer ON")
			self.conn.turnOn_btn()
			return flask.jsonify(res="Turning the 3D printer on. Please wait ... ")

		elif command == "turnOff":
			self._logger.info("Turning the printer OFF")
			self.conn.shutdown_btn()
			return flask.jsonify(res="Turning the 3D printer off. 3 ... 2 ... 1 ....")
		# Triggered when the user clicks to 'update connection' within the settings interface
		elif command == "update":
			try:
				self.on_settings_save(data)
				returnData = self.conn.get_plug_information()
				self._logger.info(returnData)
				return flask.jsonify(res=self.conn.get_plug_information())
			except:
				return flask.jsonify(res="Error Occurred")

	def get_settings_defaults(self):
		return dict(
			url="0.0.0.0",
			device="Please Update Connection",
			firmwareVersion="Please Update Connection",
			auto=True,
			movieDone=True
		)

	def on_settings_save(self, data):
		try:
			self._logger.info(data)
			if data["url"] != self._settings.get(["url"]):
				self._logger.info("++++=")
				self.conn.__init__(data["url"])
				self.conn.update_two()
		except:
			pass
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

	def get_template_configs(self):
		return [
			dict(type="navbar", template="TpNavigation_navbar.jinja2"),
			dict(type="settings", template="TpNavigation_settings.jinja2", custom_bindings=False),
		]

	# Setting the location of the assets such as javascript
	def get_assets(self):
		return dict(
			js=["js/navbarControll.js", "js/settingsControll.js"],
			css=["css/settingsControll.css", "css/navbarControll.css"],
		)

	# This is being used to distribute updates
	def get_update_information(self):
		return dict(
			TpLinkHandler=dict(
				display_name="TpLinkHandler",
				display_version=self._plugin_version,

				type="github_release",
				user="jamesmccannon02",
				repo="OctoPrint-Tplinkautoshutdown",
				current=self._plugin_version,

				pip="https://github.com/jamesmccannon02/OctoPrint-Tplinkautoshutdown/archive/{target_version}.zip"
			)
		)


__plugin_name__ = "TpLinkHandler"
__plugin_pythoncompat__ = ">=3.7,<4"
__plugin_implementation__ = TpLinkAutoShutdown()
__plugin_hooks__ = {
	"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}
