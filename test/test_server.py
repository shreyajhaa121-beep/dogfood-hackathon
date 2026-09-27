
import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import server


TEST_DATA = {
    "projects": [
        {
            "id": "test-project-1",
            "title": "Test Project",
            "summary": "A project used for automated testing.",
            "team": "test-team",
            "track": "test-track",
            "repo_url": "https://github.com/example/test-project",
        }
    ],
    "scores": [
        {
            "judge_id": "judge_a",
            "project_id": "test-project-1",
            "score": 8,
        },
        {
            "judge_id": "judge_b",
            "project_id": "test-project-1",
            "score": 7,
        },
    ],
}


class PortalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture_patch = patch(
            "server.load_fixtures",
            return_value=TEST_DATA,
        )
        cls.fixture_patch.start()

        cls.httpd = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            server.PortalHandler,
        )
        cls.port = cls.httpd.server_address[1]

        cls.thread = threading.Thread(
            target=cls.httpd.serve_forever,
            daemon=True,
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()
        cls.fixture_patch.stop()

    def request(self, method, path, token=None):
        connection = http.client.HTTPConnection(
            "127.0.0.1",
            self.port,
            timeout=5,
        )

        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        connection.request(method, path, headers=headers)
        response = connection.getresponse()
        status = response.status
        body = response.read().decode("utf-8")
        content_type = response.getheader("Content-Type", "")
        connection.close()

        return status, body, content_type

    def test_public_gallery_shows_project(self):
        status, body, content_type = self.request(
            "GET",
            "/projects",
        )

        self.assertEqual(status, 200)
        self.assertIn("Test Project", body)
        self.assertIn("/project?id=test-project-1", body)
        self.assertIn("text/html", content_type)

    def test_project_details_page(self):
        status, body, _ = self.request(
            "GET",
            "/project?id=test-project-1",
        )

        self.assertEqual(status, 200)
        self.assertIn("Test Project", body)
        self.assertIn("test-team", body)
        self.assertIn("test-track", body)
        self.assertIn("Open project repository", body)

    def test_unknown_project_returns_404(self):
        status, body, _ = self.request(
            "GET",
            "/project?id=missing-project",
        )

        self.assertEqual(status, 404)
        self.assertIn("Project not found", body)

    def test_judge_can_view_own_scores(self):
        status, body, _ = self.request(
            "GET",
            "/api/judge/scores",
            token="judge-a-demo",
        )

        self.assertEqual(status, 200)
        self.assertIn("judge_a", body)
        self.assertNotIn("judge_b", body)

    def test_participant_cannot_view_judge_scores(self):
        status, body, _ = self.request(
            "GET",
            "/api/judge/scores",
            token="participant-demo",
        )

        self.assertEqual(status, 403)
        self.assertIn("Judge access required", body)

    def test_judge_cannot_view_another_judges_scores(self):
        status, body, _ = self.request(
            "GET",
            "/api/judge/scores?judge=judge_a",
            token="judge-b-demo",
        )

        self.assertEqual(status, 403)
        self.assertIn("another judge", body)

    def test_organizer_can_export_csv(self):
        status, body, content_type = self.request(
            "GET",
            "/api/export.csv",
            token="organizer-demo",
        )

        self.assertEqual(status, 200)
        self.assertIn("text/csv", content_type)
        self.assertIn("test-project-1", body)
        self.assertIn("Test Project", body)

    def test_participant_cannot_export_csv(self):
        status, body, _ = self.request(
            "GET",
            "/api/export.csv",
            token="participant-demo",
        )

        self.assertEqual(status, 403)
        self.assertIn("Organizer access required", body)

    def test_closed_event_rejects_submission(self):
        status, body, _ = self.request(
            "POST",
            "/projects/new",
            token="participant-demo",
        )

        self.assertEqual(status, 409)
        self.assertIn("Submission period is closed", body)


if __name__ == "__main__":
    unittest.main()
  
